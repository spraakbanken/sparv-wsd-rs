"""Word sense disambiguation based on SALDO annotation."""

import subprocess
import typing as t
from pathlib import Path

from sparv.api import (
    Annotation,
    Binary,
    Config,
    Model,
    ModelOutput,
    Output,
    annotator,
    get_logger,
    modelbuilder,
    util,
)

logger = get_logger(__name__)

SENT_SEP = "$SENT$"


@annotator(
    "Word sense disambiguation",
    language=["swe"],
    config=[
        Config(
            "sparv_wsd_rs.sense_model",
            default="sparv_wsd_rs/ALL_512_128_w10_A2_140403_ctx1.bin",
            description="Path to sense model",
        ),
        Config(
            "sparv_wsd_rs.context_model",
            default="sparv_wsd_rs/lem_cbow0_s512_w10_NEW2_ctx.bin",
            description="Path to context model",
        ),
        Config(
            "sparv_wsd_rs.default_prob",
            -1.0,
            description="Default value for unanalyzed senses",
        ),
        Config(
            "sparv_wsd_rs.bin",
            default="wsd-rs/saldowsd",
            description="Path name of the executable file",
        ),
        Config(
            "sparv_wsd_rs.prob_format",
            util.constants.SCORESEP + "%.3f",
            description="Format string for how to print the sense probability",
        ),
    ],
)
def annotate(
    wsdbin: Binary = Binary("[sparv_wsd_rs.bin]"),
    sense_model: Model = Model("[sparv_wsd_rs.sense_model]"),
    context_model: Model = Model("[sparv_wsd_rs.context_model]"),
    out: Output = Output(
        "<token>:sparv_wsd_rs.sense_rs",
        cls="token:sense",
        description="Sense disambiguated SALDO identifiers",
    ),
    sentence: Annotation = Annotation("<sentence>"),
    word: Annotation = Annotation("<token:word>"),
    ref: Annotation = Annotation("<token:ref>"),
    lemgram: Annotation = Annotation("<token>:saldo.lemgram"),
    saldo: Annotation = Annotation("<token>:saldo.sense"),
    pos: Annotation = Annotation("<token:pos>"),
    token: Annotation = Annotation("<token>"),
    prob_format: str = Config("sparv_wsd_rs.prob_format"),
    default_prob: float = Config("sparv_wsd_rs.default_prob"),  # type: ignore [assignment]
    encoding: str = util.constants.UTF8,
) -> None:
    """Run the word sense disambiguation tool (saldowsd) to add probabilities to the saldo annotation.

    Unanalyzed senses (e.g. multiword expressions) receive the probability value given by default_prob.
      - wsdjar is the name of the java programme to be used for the wsd
      - sense_model and context_model are the models to be used with wsdjar
      - out is the resulting annotation file
      - sentence is an existing annotation for sentences and their children (words)
      - word is an existing annotations for wordforms
      - ref is an existing annotation for word references
      - lemgram and saldo are existing annotations for inflection tables and meanings
      - pos is an existing annotations for part-of-speech
      - prob_format is a format string for how to print the sense probability
      - default_prob is the default value for unanalyzed senses
    """
    word_annotation = list(word.read())
    ref_annotation = list(ref.read())
    lemgram_annotation = list(lemgram.read())
    saldo_annotation = list(saldo.read())
    pos_annotation = list(pos.read())

    sentences, orphans = sentence.get_children(token)
    sentences.append(orphans)
    # Remove empty sentences
    sentences = [s for s in sentences if s]

    # Start WSD process
    process = wsd_start(wsdbin, sense_model.path, context_model.path, encoding)

    # Construct input and send to WSD
    stdin = build_input(
        sentences,
        word_annotation,
        ref_annotation,
        lemgram_annotation,
        saldo_annotation,
        pos_annotation,
    )

    if encoding:
        stdin = stdin.encode(encoding)

    stdout, stderr = process.communicate(stdin)
    # TODO: Solve hack line below!
    # Problem is that regular messages "Reading sense vectors.." are also piped to stderr.
    logger.debug("stdout = %s", stdout)
    logger.debug("stderr = %s", stderr)
    if len(stderr) > 52:  # noqa: PLR2004
        util.system.kill_process(process)
        logger.error(str(stderr))
        return

    if encoding:
        stdout = stdout.decode(encoding)

    process_output(word, out, stdout, sentences, saldo_annotation, prob_format, default_prob)

    # Kill running subprocess
    util.system.kill_process(process)
    return


@modelbuilder("WSD models", language=["swe"])
def build_model(
    sense_model: ModelOutput = ModelOutput("sparv_wsd_rs/ALL_512_128_w10_A2_140403_ctx1.bin"),
    context_model: ModelOutput = ModelOutput("sparv_wsd_rs/lem_cbow0_s512_w10_NEW2_ctx.bin"),
) -> None:
    """Download models for SALDO-based word sense disambiguation."""
    # Download sense model
    sense_model.download(
        "https://github.com/spraakbanken/sparv-wsd/raw/master/models/scouse/ALL_512_128_w10_A2_140403_ctx1.bin"
    )

    # Download context model
    context_model.download(
        "https://github.com/spraakbanken/sparv-wsd/raw/master/models/scouse/lem_cbow0_s512_w10_NEW2_ctx.bin"
    )


def wsd_start(
    wsdbin: Binary, sense_model: Path, context_model: Path, encoding: str
) -> tuple[str, str] | subprocess.Popen:
    """Start a wsd process and return it."""
    wsd_args = [
        ("-appName", "se.gu.spraakbanken.wsd.VectorWSD"),
        ("-format", "tab"),
        ("-svFile", sense_model),
        ("-cvFile", context_model),
        ("-s1Prior", "1"),
        ("-decay", "true"),
        ("-contextWidth", "10"),
        ("-verbose", "false"),
    ]
    arguments = [f"{a[0]}={a[1]}" if isinstance(a, tuple) else a for a in wsd_args]

    return util.system.call_binary(wsdbin, arguments, encoding=encoding, return_command=True)


def build_input(
    sentences: list,
    word_annotation: list[str],
    ref_annotation: list[str],
    lemgram_annotation: list[str],
    saldo_annotation: list[str],
    pos_annotation: list[str],
) -> str:
    """Construct tab-separated input for WSD."""
    rows = []
    for sentence in sentences:
        for token_index in sentence:
            mwe = False
            word = word_annotation[token_index]
            ref = ref_annotation[token_index]
            pos = pos_annotation[token_index].lower()
            saldo = (
                saldo_annotation[token_index].strip(util.constants.AFFIX)
                if saldo_annotation[token_index] != util.constants.AFFIX
                else "_"
            )
            if "_" in saldo and len(saldo) > 1:
                mwe = True

            lemgram, simple_lemgram = make_lemgram(lemgram_annotation[token_index], word, pos)

            if mwe:
                lemgram = remove_mwe(lemgram)
                simple_lemgram = remove_mwe(simple_lemgram)
                saldo = remove_mwe(saldo)
            row = f"{ref}\t{word}\t_\t{lemgram}\t{simple_lemgram}\t{saldo}"
            rows.append(row)
        # Append empty row as sentence separator
        rows.append(f"_\t_\t_\t_\t{SENT_SEP}\t_")
    return "\n".join(rows)


def process_output(
    word: Annotation,
    out: Output,
    stdout: t.Any,
    in_sentences: list,
    saldo_annotation: list[str],
    prob_format: str,
    default_prob: float,
) -> None:
    """Parse WSD output and write annotation."""
    out_annotation = word.create_empty_attribute()

    # Split output into sentences
    out_sentences = stdout.strip()
    out_sentences = out_sentences.split(f"_\t_\t_\t_\t{SENT_SEP}\t_\t_")
    out_sentences = [i for i in out_sentences if i]

    # Split output into tokens
    for out_sent, in_sent in zip(out_sentences, in_sentences, strict=True):  # noqa: PLR1702
        out_tokens = [t for t in out_sent.split("\n") if t]
        for out_tok, in_tok in zip(out_tokens, in_sent, strict=True):
            out_toks = out_tok.split("\t")
            out_prob = [i for i in out_toks[6].split("|") if i != "_"]
            out_meanings = [i for i in out_toks[5].split("|") if i != "_"]
            saldo = [i for i in saldo_annotation[in_tok].strip(util.constants.AFFIX).split(util.constants.DELIM) if i]
            logger.debug("out_meanings=%s, out_prob = %s", out_meanings, out_prob)

            new_saldo = []
            if out_prob:
                for meaning in saldo:
                    if meaning in out_meanings:
                        i = out_meanings.index(meaning)
                        try:
                            new_saldo.append((meaning, float(out_prob[i])))
                        except ValueError as exc:
                            logger.error(
                                "Failed to convert prob[%d] for '%s': '%s'",
                                i,
                                meaning,
                                exc,
                            )
                            raise
                    else:
                        new_saldo.append((meaning, default_prob))
            else:
                new_saldo = [(meaning, default_prob) for meaning in saldo]

            # Sort by probability
            new_saldo.sort(key=lambda x: (-x[1], x[0]))
            # Format probability according to prob_format
            new_saldo = [saldo + prob_format % prob if prob_format else saldo for saldo, prob in new_saldo]
            out_annotation[in_tok] = util.misc.cwbset(new_saldo)  # type: ignore [arg-type]

    out.write(out_annotation)


def make_lemgram(lemgram: str, word: str, pos: str) -> tuple[str, str]:
    """Construct lemgram and simple_lemgram format."""
    lemgram = lemgram.strip(util.constants.AFFIX) if lemgram != util.constants.AFFIX else "_"
    simple_lemgram = util.constants.DELIM.join({lem[: lem.rfind(".")] for lem in lemgram.split(util.constants.DELIM)})

    # Fix simple lemgram for tokens without lemgram (word + pos)
    if not simple_lemgram:
        simple_lemgram = word + ".." + pos
    return lemgram, simple_lemgram


def remove_mwe(annotation: str) -> str:
    """For MWEs: strip unnecessary information."""
    annotation_ = annotation.split(util.constants.DELIM)
    annotation_ = [i for i in annotation_ if "_" not in i]
    if annotation_:
        return util.constants.DELIM.join(annotation_)
    return "_"
