/****************************************************************************
 * examples/module.c
 * 
 * Generated from examples/module.toml
 * By binding.py @ 2021-03-22 16:55:43.950862
 *
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.  The
 * ASF licenses this file to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance with the
 * License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
 * License for the specific language governing permissions and limitations
 * under the License.
 *
 ****************************************************************************/

/****************************************************************************
 * Included Files
 ****************************************************************************/

#include <stdio.h>
#include <alloca.h>
#include <string.h>

#include "duktape.h"

/****************************************************************************
 * Private Functions
 ****************************************************************************/

static duk_ret_t js_print(duk_context *ctx)
{
  const char *p0;

  p0 = duk_to_string(ctx, 0);

  printf(p0);

  return 0;
}

static duk_ret_t js_log(duk_context *ctx)
{
  const char *p0;

  p0 = duk_to_string(ctx, 0);

  printf(p0);

  return 0;
}

static duk_ret_t js_sum(duk_context *ctx)
{
  int ret;
  int p0;
  int p1;
  int p2;

  p0 = duk_to_int(ctx, 0);
  p1 = duk_to_int(ctx, 1);
  p2 = duk_to_int(ctx, 2);

  ret = sum(p0, p1, p2);
  duk_push_int(ctx, ret);

  return 1;
}

/****************************************************************************
 * Public Functions
 ****************************************************************************/

void js_binding_init(duk_context *ctx)
{
  int idx = 0;
  duk_push_c_function(ctx, js_print, 1);
  duk_put_global_string(ctx, "print");

  duk_push_int(ctx, 16);
  duk_put_global_string(ctx, "MAXJOBS");


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
}
