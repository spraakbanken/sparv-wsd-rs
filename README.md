# sparv-wsd-rs

Rewrite of Sparv module sparv-wsd to use [wsd-rs](https://github.com/spraakbanken/wsd-rs) instead.

The binary `saldowsd` from `wsd-rs` can be downloaded from <https://github.com/spraakbanken/wsd-rs/releases>.

An example of the output from `Sparv` can be seen [here](./assets/small/bet-2018-2021-1-short_export.gold.xml).

The following annotations differ:

- anslag: `|anslag..1:0.993|anslag..2:0.004|anslag..3:0.004|` != `|anslag..1:0.992|anslag..3:0.004|anslag..2:0.004|`
- avvikelse: `|avvikelse..1:0.978|avvikelse..2:0.022|` != `|avvikelse..1:0.977|avvikelse..2:0.023|`
- utskottets: `|utskott..2:0.835|utskott..3:0.109|utskott..1:0.056|` != `|utskott..2:0.843|utskott..3:0.101|utskott..1:0.056|`
- särskilda: `|särskilja..1:0.587|särskild..1:0.413|` != `|särskilja..1:0.589|särskild..1:0.411|`
