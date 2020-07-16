raise NotImplementedError


""" Ported from pony/orm/core.py


                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   Copyright 2016 Alexander Kozlovsky, Alexey Malashkevich



"""

import types

from pony import options

from pony.orm.asttranslation import create_extractors
from pony.orm.core import special_functions, const_functions, extract_vars, \
    SetIterator, UseAnotherTranslator, OptimizationFailed, \
    Attribute, get_globals_and_locals, DescWrapper, string2ast
from pony.orm.decompiling import decompile
from pony.orm.ormtypes import QueryType, RawSQL
from pony.py23compat import iteritems, PY2, basestring, int_types
from pony.thirdparty.compiler import ast
from pony.utils import throw, HashableDict, pickle_ast, unpickle_ast, \
    cut_traceback, cut_traceback_depth, get_lambda_args


class Query(object):
    def __init__(query, code_key, tree, globals, locals, cells=None, left_join=False, database=None):
        assert isinstance(tree, ast.GenExprInner)
        tree, extractors = create_extractors(code_key, tree, globals, locals, special_functions, const_functions)
        filter_num = 0
        vars, vartypes = extract_vars(code_key, filter_num, extractors, globals, locals, cells)

        node = tree.quals[0].iter
        varkey = filter_num, node.src, code_key
        origin = vars[varkey]
        if isinstance(origin, Query):
            prev_query = origin
        elif isinstance(origin, SetIterator):
            prev_query = origin._query
        else:
            raise NotImplementedError
            # prev_query = None

        if prev_query is not None:
            database = prev_query._translator.database
            filter_num = prev_query._filter_num + 1
            vars, vartypes = extract_vars(code_key, filter_num, extractors, globals, locals, cells)

        query._filter_num = filter_num
        database.provider.normalize_vars(vars, vartypes)

        query._code_key = code_key
        query._key = HashableDict(code_key=code_key, vartypes=vartypes, left_join=left_join, filters=())
        query._database = database

        translator, vars = query._get_translator(query._key, vars)
        query._vars = vars

        if translator is None:
            pickled_tree = pickle_ast(tree)
            tree_copy = unpickle_ast(pickled_tree)  # tree = deepcopy(tree)
            translator_cls = database.provider.translator_cls
            try:
                translator = translator_cls(tree_copy, None, code_key, filter_num, extractors, vars, vartypes.copy(), left_join=left_join)
            except UseAnotherTranslator as e:
                translator = e.translator
            name_path = translator.can_be_optimized()
            if name_path:
                tree_copy = unpickle_ast(pickled_tree)  # tree = deepcopy(tree)
                try:
                    translator = translator_cls(tree_copy, None, code_key, filter_num, extractors, vars, vartypes.copy(),
                                                left_join=True, optimize=name_path)
                except UseAnotherTranslator as e:
                    translator = e.translator
                except OptimizationFailed:
                    translator.optimization_failed = True
            translator.pickled_tree = pickled_tree
            if translator.can_be_cached:
                database._translator_cache[query._key] = translator

        query._translator = translator
        query._filters = ()
        query._next_kwarg_id = 0
        query._for_update = query._nowait = query._skip_locked = False
        query._distinct = None

    def _get_query(query):
        return query

    def _get_type_(query):
        return QueryType(query)

    def _normalize_var(query, query_type):
        return query_type, query

    def _clone(query, **kwargs):
        new_query = object.__new__(Query)
        new_query.__dict__.update(query.__dict__)
        new_query.__dict__.update(kwargs)
        return new_query

    def _get_translator(query, query_key, vars):
        new_vars = vars.copy()
        database = query._database
        translator = database._translator_cache.get(query_key)
        all_func_vartypes = {}
        if translator is not None:
            if translator.func_extractors_map:
                for func, func_extractors in iteritems(translator.func_extractors_map):
                    func_id = id(func.func_code if PY2 else func.__code__)
                    func_filter_num = translator.filter_num, 'func', func_id
                    func_vars, func_vartypes = extract_vars(
                        func_id, func_filter_num, func_extractors, func.__globals__, {}, func.__closure__)  # todo closures
                    database.provider.normalize_vars(func_vars, func_vartypes)
                    new_vars.update(func_vars)
                    all_func_vartypes.update(func_vartypes)
                if all_func_vartypes != translator.func_vartypes:
                    return None, vars.copy()
            for key, val in iteritems(translator.fixed_param_values):
                assert key in new_vars
                if val != new_vars[key]:
                    del database._translator_cache[query_key]
                    return None, vars.copy()
        return translator, new_vars

    def _construct_sql_and_arguments(query, limit=None, offset=None, range=None, aggr_func_name=None, aggr_func_distinct=None, sep=None):
        translator = query._translator
        sql_key = HashableDict(
            query._key,
            vartypes=HashableDict(query._translator.vartypes),
            fixed_param_values=HashableDict(translator.fixed_param_values),
            limit=limit,
            offset=offset,
            distinct=query._distinct,
            aggr_func=(aggr_func_name, aggr_func_distinct, sep),
            for_update=query._for_update,
            nowait=query._nowait,
            skip_locked=query._skip_locked,
            inner_join_syntax=options.INNER_JOIN_SYNTAX,
            attrs_to_prefetch=()
        )
        database = query._database

        sql_ast, attr_offsets = translator.construct_sql_ast(
            limit, offset, query._distinct, aggr_func_name, aggr_func_distinct, sep,
            query._for_update, query._nowait, query._skip_locked)
        sql, adapter = database.provider.ast2sql(sql_ast)  # TODO: change

        arguments = adapter(query._vars)
        if query._translator.query_result_is_cacheable:
            arguments_key = HashableDict(arguments) if type(arguments) is dict else arguments
            try: hash(arguments_key)
            except: query_key = None  # arguments are unhashable
            else: query_key = HashableDict(sql_key, arguments_key=arguments_key)
        else: query_key = None
        return sql, arguments, attr_offsets, query_key

    def get_sql(query):
        sql, arguments, attr_offsets, query_key = query._construct_sql_and_arguments()
        return sql

    @cut_traceback
    def without_distinct(query):
        return query._clone(_distinct=False)

    @cut_traceback
    def distinct(query):
        return query._clone(_distinct=True)

    @cut_traceback
    def order_by(query, *args):
        return query._order_by('order_by', *args)

    @cut_traceback
    def sort_by(query, *args):
        return query._order_by('sort_by', *args)

    def _order_by(query, method_name, *args):
        if not args: throw(TypeError, '%s() method requires at least one argument' % method_name)
        if args[0] is None:
            if len(args) > 1: throw(TypeError, 'When first argument of %s() method is None, it must be the only argument' % method_name)
            tup = (('without_order',),)
            new_key = HashableDict(query._key, filters=query._key['filters'] + tup)
            new_filters = query._filters + tup

            new_translator, new_vars = query._get_translator(new_key, query._vars)
            if new_translator is None:
                new_translator = query._translator.without_order()
                query._database._translator_cache[new_key] = new_translator
            return query._clone(_key=new_key, _filters=new_filters, _translator=new_translator)

        if isinstance(args[0], (basestring, types.FunctionType)):
            func, globals, locals = get_globals_and_locals(args, kwargs=None, frame_depth=cut_traceback_depth+2)
            return query._process_lambda(func, globals, locals, order_by=True)

        if isinstance(args[0], RawSQL):
            raw = args[0]
            return query.order_by(lambda: raw)

        attributes = numbers = False
        for arg in args:
            if isinstance(arg, int_types): numbers = True
            elif isinstance(arg, (Attribute, DescWrapper)): attributes = True
            else: throw(TypeError, "order_by() method receive an argument of invalid type: %r" % arg)
        if numbers and attributes:
            throw(TypeError, 'order_by() method receive invalid combination of arguments')

        tup = (('order_by_numbers' if numbers else 'order_by_attributes', args),)
        new_key = HashableDict(query._key, filters=query._key['filters'] + tup)
        new_filters = query._filters + tup

        new_translator, new_vars = query._get_translator(new_key, query._vars)
        if new_translator is None:
            if numbers: new_translator = query._translator.order_by_numbers(args)
            else: new_translator = query._translator.order_by_attributes(args)
            query._database._translator_cache[new_key] = new_translator
        return query._clone(_key=new_key, _filters=new_filters, _translator=new_translator)

    def _process_lambda(query, func, globals, locals, order_by=False, original_names=False):
        prev_translator = query._translator
        argnames = ()
        if isinstance(func, basestring):
            func_id = func
            func_ast = string2ast(func)
            if isinstance(func_ast, ast.Lambda):
                argnames = get_lambda_args(func_ast)
                func_ast = func_ast.code
            cells = None
        elif type(func) is types.FunctionType:
            argnames = get_lambda_args(func)
            func_id = id(func.func_code if PY2 else func.__code__)
            func_ast, external_names, cells = decompile(func)
        elif not order_by: throw(TypeError,
            'Argument of filter() method must be a lambda functon or its text. Got: %r' % func)
        else: assert False  # pragma: no cover

        if argnames:
            if original_names:
                for name in argnames:
                    if name not in prev_translator.namespace: throw(TypeError,
                        'Lambda argument `%s` does not correspond to any variable in original query' % name)
            else:
                expr_type = prev_translator.expr_type
                expr_count = len(expr_type) if type(expr_type) is tuple else 1
                if len(argnames) != expr_count:
                    throw(TypeError, 'Incorrect number of lambda arguments. '
                                     'Expected: %d, got: %d' % (expr_count, len(argnames)))
        else:
            original_names = True

        new_filter_num = query._filter_num + 1
        func_ast, extractors = create_extractors(
            func_id, func_ast, globals, locals, special_functions, const_functions, argnames or prev_translator.namespace)
        if extractors:
            vars, vartypes = extract_vars(func_id, new_filter_num, extractors, globals, locals, cells)
            query._database.provider.normalize_vars(vars, vartypes)
            new_vars = query._vars.copy()
            new_vars.update(vars)
        else: new_vars, vartypes = query._vars, HashableDict()
        tup = (('order_by' if order_by else 'where' if original_names else 'filter', func_id, vartypes),)
        new_key = HashableDict(query._key, filters=query._key['filters'] + tup)
        new_filters = query._filters + (('apply_lambda', func_id, new_filter_num, order_by, func_ast, argnames, original_names, extractors, None, vartypes),)

        new_translator, new_vars = query._get_translator(new_key, new_vars)
        if new_translator is None:
            prev_optimized = prev_translator.optimize
            new_translator = prev_translator.apply_lambda(func_id, new_filter_num, order_by, func_ast, argnames, original_names, extractors, new_vars, vartypes)
            if not prev_optimized:
                name_path = new_translator.can_be_optimized()
                if name_path:
                    tree_copy = unpickle_ast(prev_translator.pickled_tree)  # tree = deepcopy(tree)
                    translator_cls = prev_translator.__class__
                    try:
                        new_translator = translator_cls(
                            tree_copy, None, prev_translator.original_code_key, prev_translator.original_filter_num,
                            prev_translator.extractors, None, prev_translator.vartypes.copy(),
                            left_join=True, optimize=name_path)
                    except UseAnotherTranslator:
                        assert False
                    new_translator = query._reapply_filters(new_translator)
                    new_translator = new_translator.apply_lambda(func_id, new_filter_num, order_by, func_ast, argnames, original_names, extractors, new_vars, vartypes)
            query._database._translator_cache[new_key] = new_translator
        return query._clone(_filter_num=new_filter_num, _vars=new_vars, _key=new_key, _filters=new_filters,
                            _translator=new_translator)

    def _reapply_filters(query, translator):
        for tup in query._filters:
            method_name, args = tup[0], tup[1:]
            translator_method = getattr(translator, method_name)
            translator = translator_method(*args)
        return translator

    @cut_traceback
    def filter(query, *args, **kwargs):
        if args:
            if isinstance(args[0], RawSQL):
                raw = args[0]
                return query.filter(lambda: raw)
            func, globals, locals = get_globals_and_locals(args, kwargs, frame_depth=cut_traceback_depth+1)
            return query._process_lambda(func, globals, locals, order_by=False)
        if not kwargs: return query
        return query._apply_kwargs(kwargs)

    @cut_traceback
    def where(query, *args, **kwargs):
        if args:
            if isinstance(args[0], RawSQL):
                raw = args[0]
                return query.where(lambda: raw)
            func, globals, locals = get_globals_and_locals(args, kwargs, frame_depth=cut_traceback_depth+1)
            return query._process_lambda(func, globals, locals, order_by=False, original_names=True)
        if not kwargs: return query

        if len(query._translator.tree.quals) > 1: throw(TypeError,
            'Keyword arguments are not allowed: query iterates over more than one entity')
        return query._apply_kwargs(kwargs, original_names=True)

    def _apply_kwargs(query, kwargs, original_names=False):
        translator = query._translator
        if original_names:
            tablerefs = translator.sqlquery.tablerefs
            alias = translator.tree.quals[0].assign.name
            tableref = tablerefs[alias]
            entity = tableref.entity
        else:
            entity = translator.expr_type
        get_attr = entity._adict_.get
        filterattrs = []
        value_dict = {}
        next_id = query._next_kwarg_id
        for attrname, val in sorted(iteritems(kwargs)):
            attr = get_attr(attrname)
            if attr is None: throw(AttributeError,
                'Entity %s does not have attribute %s' % (entity.__name__, attrname))
            if attr.is_collection: throw(TypeError,
                '%s attribute %s cannot be used as a keyword argument for filtering'
                % (attr.__class__.__name__, attr))
            val = attr.validate(val, None, entity, from_db=False)
            id = next_id
            next_id += 1
            filterattrs.append((attr, id, val is None))
            value_dict[id] = val

        filterattrs = tuple(filterattrs)
        tup = (('apply_kwfilters', filterattrs, original_names),)
        new_key = HashableDict(query._key, filters=query._key['filters'] + tup)
        new_filters = query._filters + tup
        new_vars = query._vars.copy()
        new_vars.update(value_dict)
        new_translator, new_vars = query._get_translator(new_key, new_vars)
        if new_translator is None:
            new_translator = translator.apply_kwfilters(filterattrs, original_names)
            query._database._translator_cache[new_key] = new_translator
        return query._clone(_key=new_key, _filters=new_filters, _translator=new_translator,
                            _next_kwarg_id=next_id, _vars=new_vars)

    @cut_traceback
    def for_update(query, nowait=False, skip_locked=False):
        if nowait and skip_locked:
            throw(TypeError, 'nowait and skip_locked options are mutually exclusive')
        return query._clone(_for_update=True, _nowait=nowait, _skip_locked=skip_locked)
