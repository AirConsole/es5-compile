# es5-compile
Compiles ES6 to ES5 and minifies it using Googles Closure Compiler.

Usage:

`es5-compile.py path_to_build.json`

## build.json format

### Minimal build.json

```
{
  "output": "output.js"
}
```
This will take all files in the `src` directory and compile them into `output.js`

### Source files
```
{
  "output": "output.js",
  "src": ["file1.js", "file2.js", "directory1", "directory2"]
}
```

`src` specifies a list of files and directories to be included in the compilation (order guaranteed). If you add a directory then all files in the directory and subdirectories will be included in alphabetical order.
Only files ending in `.js` are included. If a file appears multiple times (e.g. you include the file and then the directory of the file), then it is only added the first time it is seen.

### Exlude files

```
{
  "output": "output.js",
  "src": ["file1.js", "file2.js", "directory1", "directory2"],
  "exlucde": ["directory1/bad_file.js", "directory2/bad_file_subdirectory"]
}
```

`exclude` specifies a list of files and directories to be excluded from the compilation. Is convenient when you want to include a whole directory except for a few files.

### Header 
```
{
  "output": "output.js",
  "header": "/* Copyright by Your Company */"
}
```

`header` adds some code in the beginning of your file

### Adding additional Namespaces

```
{
  "output": "output.js",
  "src": ["src/libs"],
  "namespace": {
    "src/libs/engine.io.js": "BiggerLib.eio"
  }
}
```

`namespace` is a mapping from filename to an additional namespace prefix. For example, `engine.io.js` would export its module in the global namespace under `eio`. The config above would export it under `BiggerLib.eio`

### Debugging

```
{
  "output": "output.js",
  "compile": false
}
```

If you set `compile` to `false` then the files are not compiled, but only concatenated into one big file. Convenient for debugging.
