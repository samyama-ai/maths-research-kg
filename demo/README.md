# Demo

Narrated walkthrough of the Maths Research KG on a fast, real subset.

```bash
python -m demo.demo
```
Record/regenerate:
```bash
asciinema rec --overwrite --cols 92 --rows 32 --idle-time-limit 2.0 \
  -c "bash -c 'python -m demo.demo'" demo/maths_research.cast
agg demo/maths_research.cast demo/maths_research.gif
```
