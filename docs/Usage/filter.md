# Pandoc --filter option

pandoc-math can also be used just like any other pandoc filter.

A typical command using pandoc-math with the filter option would look like:

``` linenums="1"
pandoc main.tex -o output.html -s --mathjax --number-sections --filter pandoc-math --metadata-file metadata.yaml
```


> NOTE: **Specifying metadata**
>
> To get support for amsthm environments, you will need to specify the amsthm theoren names, styles,
> and shared/parent counters options manually in a YAML file and pass this to the `--metadata-file`
> option. An example of such a metadata file can be found [here](../examples/Example paper/metadata.yaml).
