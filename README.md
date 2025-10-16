# sparv-wsd-rs

Rewrite of Sparv module sparv-wsd to use [saldowsd-rs](https://github.com/spraakbanken/saldowsd-rs) instead.

The binary `saldowsd` from `saldowsd-rs` can be downloaded from <https://github.com/spraakbanken/saldowsd-rs/releases>.

An example of the output from `Sparv` can be seen [here](./assets/small/bet-2018-2021-1-short_export.gold.xml).

The following annotations differ:

- anslag: `|anslag..1:0.993|anslag..2:0.004|anslag..3:0.004|` != `|anslag..1:0.992|anslag..3:0.004|anslag..2:0.004|`
- avvikelse: `|avvikelse..1:0.978|avvikelse..2:0.022|` != `|avvikelse..1:0.977|avvikelse..2:0.023|`
- utskottets: `|utskott..2:0.835|utskott..3:0.109|utskott..1:0.056|` != `|utskott..2:0.843|utskott..3:0.101|utskott..1:0.056|`
- särskilda: `|särskilja..1:0.587|särskild..1:0.413|` != `|särskilja..1:0.589|särskild..1:0.411|`

## Sparv stats

The example [`small`](./examples/small) indicates that using `saldowsd` is faster than `saldowsd.jar`:

```shell
> sparv run --stats

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 🐦 100% 13 of 13 tasks Total time: 0:00:16

The exported files can be found in the following location:
 • export/xml_export.pretty/

  Task                      Time taken   Percentage
  hunpos:msdtag                0:00:05        33.1%
  wsd:annotate                 0:00:02        16.7%
  saldo:annotate               0:00:02        12.6%
  sparv_wsd_rs:annotate        0:00:02        12.0%
  segment:sentence             0:00:01         4.4%
  segment:tokenize             0:00:01         4.2%
  hunpos:postag                0:00:01         4.0%
  xml_export:pretty            0:00:00         2.9%
  misc:file_id                 0:00:00         2.7%
  xml_import:parse             0:00:00         2.5%
  misc:text_spans              0:00:00         2.4%
  misc:make_ref                0:00:00         2.3%
```
