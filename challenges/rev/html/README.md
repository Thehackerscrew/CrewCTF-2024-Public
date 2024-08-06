# Challenge
JS source code published in [stages](stages/).


# Transpiler usage
```
npm i jsdom acorn acorn-walk
node transpiler.js
```


# Note

The transpiler is quite janky and doesn't support a lot of JS constructs. For example, using an expression like `i++` will lead to an infinite loop. To see which constructs are supported, check out the scripts in the [stages](stages/) directory.
