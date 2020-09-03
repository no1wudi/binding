# Language Binding Generator

查看用法可以用以下命令：
```
python binding.py -h
```

目前支持生成Duktape的绑定，计划支持QuickJS、JerryScript、WASM3、WAMR、Lua。

## 语法

脚本支持全局函数、模块、常量定义的生成。

### include

指定包含文件：
```
[include]
system = ["stdio.h", "stdbool.h"]
custom = ["string.h", "demo.h"]
```

生成代码：
```
#include <stdio.h>
#include <stdbool.h>

#include "string.h"
#include "demo.h"
```

### 全局函数

```
[global.function]
print="void printf(const char *)"
```

生成代码：
```
duk_push_c_function(ctx, js_print, 1);
duk_put_global_string(ctx, "print");
```

JavaScript:
```
print('Hello -- from Bindgen!\n')
```

### 全局常量

```
[global.const]
MAXJOBS=16
```

生成代码：
```
duk_push_int(ctx, 16);
duk_put_global_string(ctx, "MAXJOBS");
```

JavaScript:
```
print(MAXJOBS)
```

### 模块

```
[console.function]
log='void printf(const char *)'

[console.const]
INFO='Information'
```

生成代码：
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
