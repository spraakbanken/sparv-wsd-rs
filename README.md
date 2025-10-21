# sparv-wsd-rs

Rewrite of Sparv module sparv-wsd to use [saldowsd-rs](https://github.com/spraakbanken/saldowsd-rs) instead.

Uses [`saldowsd` from PyPI](https://pypi.org/project/saldowsd) to automatically install the `saldowsd` binary.

## Faster than using `saldowsd.jar`

The running time for `sparv_wsd_rs` that uses `saldowsd-rs` is 12.8% faster than using Java version. See results from
running both annotations on `vivill` on our server `wombat`.

```bash
[fksparv@wombat vivill]$ sparv run --stats

  Task                                                           Time taken   Percentage
  swener:annotate                                                   5:28:09        36.1%
  sbx_sentence_sentiment_kb_sent:annotate_sentence_sentiment        1:45:36        11.6%
  sbx_emotions_kb_emoclass:annotate_sentence                        1:44:47        11.5%
  saldo:compound                                                    1:44:39        11.5%
  stanza:annotate_swe                                               1:08:54         7.6%
  geo:contextual                                                    0:33:31         3.7%
  hunpos:msdtag                                                     0:31:50         3.5%
  saldo:annotate                                                    0:26:25         2.9%
  wsd:annotate                                                      0:11:25         1.3%
  sparv_wsd_rs:annotate                                             0:09:57         1.1%
```

## Memory usage

Loading models and running a simple example (not using Sparv for this). Rust version uses 35% less memory.
Measured with [`heaptrack`](https://github.com/KDE/heaptrack).

| Tool                  | Top-RSS |
| --------------------- | ------: |
| `saldowsd` (Rust)     |  914 Mb |
| `saldowsd.jar` (Java) |  1.4 Gb |

The binary `saldowsd` from `saldowsd-rs` can be downloaded from <https://github.com/spraakbanken/saldowsd-rs/releases>.

An example of the output from `Sparv` can be seen [here](./assets/small/bet-2018-2021-1-short_export.gold.xml).

The annotations are probalistic, so they always differ a bit (wsd.sense differs with itself for different runs).

Example of differences:

- anslag: `|anslag..1:0.993|anslag..2:0.004|anslag..3:0.004|` != `|anslag..1:0.992|anslag..3:0.004|anslag..2:0.004|`
- avvikelse: `|avvikelse..1:0.978|avvikelse..2:0.022|` != `|avvikelse..1:0.977|avvikelse..2:0.023|`
- utskottets: `|utskott..2:0.835|utskott..3:0.109|utskott..1:0.056|` != `|utskott..2:0.843|utskott..3:0.101|utskott..1:0.056|`
- särskilda: `|särskilja..1:0.587|särskild..1:0.413|` != `|särskilja..1:0.589|särskild..1:0.411|`
