# Language Binding Generator

For help：
```
python binding.py -h
```

Now only Duktape supported.

## Syntax

### include

```
[include]
system = ["stdio.h", "stdbool.h"]
custom = ["string.h", "demo.h"]
```

Generated：
```
#include <stdio.h>
#include <stdbool.h>

#include "string.h"
#include "demo.h"
```

### Gloabal function

```
[global.function]
# This 'void' means ignore the return value in generated code
print="void printf(const char *)"
```

Generated：
```
duk_push_c_function(ctx, js_print, 1);
duk_put_global_string(ctx, "print");
```

Usage in JavaScript:
```
print('Hello -- from Bindgen!\n')
```

### Global constant

```
[global.const]
MAXJOBS=16
```

Generated：
```
duk_push_int(ctx, 16);
duk_put_global_string(ctx, "MAXJOBS");
```

Usage in JavaScript:
```
print(MAXJOBS)
```

### Module organization

JavaScript/Wasm has the concept of module, 

```
[console.function]
log='void printf(const char *)'

[console.const]
INFO='Information'
```

Generated：
```
duk_push_object(ctx);
idx = duk_get_top_index(ctx);
duk_push_string(ctx, "log");
duk_push_c_function(ctx, js_log, 1);
duk_def_prop(ctx, idx, DUK_DEFPROP_HAVE_VALUE);
duk_push_string(ctx, "sum");
duk_push_c_function(ctx, js_sum, 3);
duk_def_prop(ctx, idx, DUK_DEFPROP_HAVE_VALUE);
duk_push_string(ctx, "INFO");
duk_push_string(ctx, "Information");
duk_def_prop(ctx, idx, DUK_DEFPROP_HAVE_VALUE);
duk_put_global_string(ctx, "console");
```

JavaScript:
```
console.log(console.INFO)
```
