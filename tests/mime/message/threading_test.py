# coding:utf-8
"""
Fun begins here!
"""

from ... import *
from nose.tools import *
from mock import *

from flanker.mime import create
from flanker.mime.message.threading import *
from flanker.mime.message.headers import MessageId

@patch.object(MessageId, 'is_valid', Mock(return_value=True))
def test_wrapper_creates_message_id():
    message = create.text('plain','hey')
    w = Wrapper(message)
    ok_(w.message_id)
    eq_([], w.references)

@patch.object(MessageId, 'is_valid', Mock(return_value=True))
def test_wrapper_references():
    message = create.text('plain','hey')
    message.headers['References'] = '<1> <2> <3>'
    message.headers['Message-Id'] = '<4>'
    w = Wrapper(message)
    eq_('4', w.message_id)
    eq_(['1', '2', '3'], w.references)

@patch.object(MessageId, 'is_valid', Mock(return_value=True))
def test_wrapper_in_reply_to():
    message = create.text('plain','hey')
    message.headers['In-Reply-To'] = '<3>'
    message.headers['Message-Id'] = '<4>'
    w = Wrapper(message)
    eq_('4', w.message_id)
    eq_(['3'], w.references)

@patch.object(MessageId, 'is_valid', Mock(return_value=True))
def test_container_to_string():
    eq_('dummy', str(Container()))
    eq_('123@gmail.com', str(tc('123@gmail.com')))

@patch.object(MessageId, 'is_valid', Mock(return_value=True))
def test_container_is_dummy():
    ok_(Container().is_dummy)
    assert_false(tc('1').is_dummy)

@patch.object(MessageId, 'is_valid', Mock(return_value=True))
def test_container_in_root_set():
    c = Container()
    c.parent = Container()
    ok_(c.in_root_set)

    c.parent.parent = Container()
    assert_false(c.in_root_set)

@patch.object(MessageId, 'is_valid', Mock(return_value=True))
def test_container_children():
    c = Container()
    assert_false(c.has_children)
    assert_false(c.has_one_child)

    c.child = Container()
    ok_(c.has_children)
    ok_(c.has_one_child)

    c.child.next = Container()
    ok_(c.has_children)
    assert_false(c.has_one_child)

@patch.object(MessageId, 'is_valid', Mock(return_value=True))
def test_container_find_and_iter_children():
    c = Container()
    eq_(None, c.last_child)
    collected = []
    for child in c.iter_children():
        collected.append(child)

    eq_([], collected)
    assert_false(c.has_descendant(None))
    assert_false(c.has_descendant(c))

    c1,c2 = Container(), Container()
    c.child = c1
    eq_(c1, c.last_child)
    ok_(c.has_descendant(c1))
    assert_false(c.has_descendant(c2))

    c.child.next = c2
    eq_(c2, c.last_child)
    ok_(c.has_descendant(c2))

    collected = []
    for child in c.iter_children():
        collected.append(child)
    eq_([c1,c2], collected)

    c3, c4, c5, c6 = make_empty(4)
    c2.child = c3
    c2.child.child = c4
    c2.child.child.next = c5
    c2.child.child.next.next = c6
    ok_(c.has_descendant(c3))
    ok_(c.has_descendant(c4))
    ok_(c.has_descendant(c5))
    ok_(c.has_descendant(c6))

@patch.object(MessageId, 'is_valid', Mock(return_value=True))
def test_container_add_child():
    c, c1, c2 = make_empty(3)

    c.add_child(c1)
    eq_(c, c1.parent)
    eq_(c1, c.child)
    eq_(None, c1.prev)

    c.add_child(c2)
    eq_(c2, c.child)
    eq_(c1, c2.next)
    eq_(c2, c1.prev)
    eq_(c, c2.parent)
    eq_(None, c2.prev)

@patch.object(MessageId, 'is_valid', Mock(return_value=True))
def test_container_remove_child():
    c, c1, c2 = make_empty(3)

    c.add_child(c1)
    c.remove_child(c1)
    eq_(None, c.child)
    eq_(None, c1.parent)
    eq_(None, c1.prev)
    eq_(None, c1.next)


    c, c1, c2 = make_empty(3)

    c.add_child(c1)
    c.add_child(c2)
    c.remove_child(c1)
    eq_(c2, c.child)
    eq_(None, c2.next)
    eq_(None, c1.prev)


    c, c1, c2 = make_empty(3)

    c.add_child(c1)
    c.add_child(c2)
    c.remove_child(c2)
    eq_(c1, c.child)
    eq_(None, c1.prev)
    eq_(None, c1.next)

    c, c1, c2, c3 = make_empty(4)

    c.add_child(c1)
    c.add_child(c2)
    c.add_child(c3)

    c.remove_child(c2)
    eq_(c3, c.child)
    eq_(c1, c3.next)
    eq_(c3, c1.prev)

@patch.object(MessageId, 'is_valid', Mock(return_value=True))
def test_container_replace_with_its_children():
    # before:
    #
    # a
    # +- b
    #    +- c - d
    #
    # read it like that: a - root, b is a's first child, c is b's first child
    #                    d is c's sibling
    #
    # after:
    #
    # a
    # +- c - d
    #
    a,b,c,d= make_empty(4)

    a.add_child(b)
    b.add_child(d)
    b.add_child(c)

    a.replace_with_its_children(b)
    eq_(c, a.child)
    eq_(d, a.child.next)

    eq_(a, c.parent)
    eq_(a, d.parent)

    eq_(None, a.child.prev)
    eq_(c, d.prev)

    # before:
    #
    # a
    # +- b - e
    #    +- c - d
    #
    # after:
    #
    # a
    # +- c - d - e
    #
    a,b,c,d,e = make_empty(5)

    a.add_child(e)
    a.add_child(b)
    b.add_child(d)
    b.add_child(c)

    a.replace_with_its_children(b)
    eq_(c, a.child)
    eq_(d, a.child.next)
    eq_(d, e.prev)
    eq_(e, d.next)
    #
    # before:
    #
    # a
    # +- b - f - e
    #        +-  c - d
    #
    #
    # after:
    #
    # a
    # +- b - c - d - e
    #
    #
    a,b,c,d,e,f = make_empty(6)

    a.add_child(e)
    a.add_child(f)
    a.add_child(b)

    f.add_child(d)
    f.add_child(c)

    a.replace_with_its_children(f)
    eq_(b, a.child)
    eq_(c, b.next)
    eq_(b, c.prev)
    eq_(d, e.prev)
    eq_(e, d.next)
    eq_(a, c.parent)
    eq_(a, d.parent)

@patch.object(MessageId, 'is_valid', Mock(return_value=True))
def test_prune_empty():
    #
    # before:
    #
    # r
    # +- b
    #    +- c1 (empty)
    #
    # after:
    #
    # r
    # +- b
    #
    b, = make_full('b')
    r, c1 = make_empty(2)
    r.add_child(b)
    b.add_child(c1)

    r.prune_empty()
    eq_(b, r.child)
    eq_(None, b.child)

    #
    # before:
    #
    # r
    # +- b
    #    +- c1 (empty)
    #       +- d
    # after:
    #
    # r
    # +- b
    #    +- d
    #
    b, d = make_full('b', 'd')
    r, c1 = make_empty(2)
    r.add_child(b)
    b.add_child(c1)
    c1.add_child(d)

    r.prune_empty()
    eq_(b, r.child)
    eq_(d, b.child)
    eq_(None, c1.parent)
    eq_(None, c1.child)

    #
    # promote child of containers with empty message and 1 child
    # directly to root level
    #
    # before:
    #
    # r
    # +- c1 (empty)
    #    +- a
    #
    # after:
    #
    # r
    # +- a
    #
    a, = make_full('a')
    r, c1 = make_empty(2)
    r.add_child(c1)
    c1.add_child(a)

    r.prune_empty()
    eq_(a, r.child)
    eq_(None, a.child)
    eq_(r, a.parent)

    #
    # do not promote child of containers with empty message and > 1 child
    # directly to root level
    #
    # before:
    #
    # r
    # +- c1 (empty)
    #    +- a - b
    #
    # after:
    #
    # r
    # +- c1 (empty)
    #    +- a - b
    #
    a,b = make_full('a', 'b')
    r, c1 = make_empty(2)
    r.add_child(c1)
    c1.add_child(b)
    c1.add_child(a)

    r.prune_empty()
    eq_(c1, r.child)
    eq_(a, c1.child)
    eq_(b, a.next)

    #
    # remove useless container
    #
    # before:
    #
    # r
    # +- c1 (empty)
    #    +- c2 (empty)
    #       +- a - b
    #
    # after:
    #
    # r
    # +- c2 (empty)
    #    +- a - b
    #
    a, b = make_full('a', 'b')
    r, c1, c2 = make_empty(3)
    r.add_child(c1)
    c1.add_child(c2)
    c2.add_child(b)
    c2.add_child(a)

    r.prune_empty()
    eq_(c2, r.child)
    eq_(a, c2.child)
    eq_(b, a.next)

    #
    # remove 2 useless containers
    #
    # before:
    #
    # r
    # +- c1 (empty)
    #    +- c2 (empty)
    #       +- c3
    #          +- a - b
    #
    # after:
    #
    # r
    # +- c3 (empty)
    #    +- a - b
    #
    a, b = make_full('a', 'b')
    r, c1, c2, c3 = make_empty(4)
    r.add_child(c1)
    c1.add_child(c2)
    c2.add_child(c3)
    c3.add_child(b)
    c3.add_child(a)

    r.prune_empty()
    eq_(c3, r.child)
    eq_(a, c3.child)
    eq_(b, a.next)


    #
    # remove 2 useless containers
    #
    # before:
    #
    # r
    # +- c1 (empty) ---- c2 (empty)
    #    +- a
    #
    # after:
    #
    # r
    # +- a
    #
    #
    a, b = make_full('a', 'b')
    r, c1, c2 = make_empty(3)
    r.add_child(c2)
    r.add_child(c1)
    c1.add_child(a)

    r.prune_empty()
    eq_(a, r.child)

    #
    # remove tons of useless containers
    #
    # before:
    #
    # r
    # +- c1 (empty) -------------- c4
    #    +- c2 (empty)
    #       +- c3 (empty)
    #          +- a ------ c
    #             +- b     +- d
    #
    # after:
    #
    # r
    # +- c3 (empty)
    #    +- a --- c
    #       +- b  +- d
    #
    a, b, c, d  = make_full('a', 'b', 'c', 'd')
    r, c1, c2, c3, c4 = make_empty(5)
    r.add_child(c4)
    r.add_child(c1)
    c1.add_child(c2)
    c2.add_child(c3)
    c3.add_child(c)
    c.add_child(d)
    c3.add_child(a)
    a.add_child(b)

    r.prune_empty()
    eq_(c3, r.child)
    eq_(None, c3.next)
    eq_(a, c3.child)
    eq_(c, a.next)

    #
    # remove megatons of useless containers
    # cN - empty containers
    #
    # before:
    #
    # r
    # +- c1
    #    +- c2---------- c6 ------- e
    #       +- c3        +- c7----- f
    #          +- c4        +- c8
    #              +- a ------ c
    #                 +- b     +- d
    #
    # after:
    #
    # r
    # +- c1
    #    +- a ---- c
    #       +- b   +- d
    a, b, c, d, e, f  = make_full('a', 'b', 'c', 'd', 'e', 'f')
    r, c1, c2, c3, c4, c5, c6, c7, c8 = make_empty(9)
    r.add_child(c1)
    c1.add_child(e)
    c1.add_child(c6)
    c6.add_child(f)
    c6.add_child(c7)
    c7.add_child(c8)
    c1.add_child(c2)
    c2.add_child(c3)
    c3.add_child(c4)
    c4.add_child(c)
    c.add_child(d)
    c4.add_child(a)
    a.add_child(b)

    r.prune_empty()
    eq_(c1, r.child)
    eq_(None, c1.next)
    eq_(a, c1.child)
    eq_(c, a.next)
    eq_(b, a.child)
    eq_(d, c.child)
    eq_(f, c.next)
    eq_(e, f.next)

@patch.object(MessageId, 'is_valid', Mock(return_value=True))
def test_introduces_loop():
    a, = make_empty(1)
    ok_(introduces_loop(a, a))

    a, b = make_empty(2)
    assert_false(introduces_loop(a, b))

    a, b = make_empty(2)
    b.add_child(a)
    ok_(introduces_loop(a, b))

    a, b, c = make_empty(3)
    b.add_child(c)
    c.add_child(a)
    ok_(introduces_loop(a, b))

@patch.object(MessageId, 'is_valid', Mock(return_value=True))
def test_build_table():
    #
    # Should create valid table for messages arriving
    # in the following order
    #
    # a
    # +- b
    #    + - c
    #        +- d
    #
    # b
    # +- c
    #    +- d
    #
    # c
    # +- d
    #
    # d
    messages = [
        make_message("a"),
        make_message("b", ["a"]),
        make_message("c", ["a", "b"]),
        make_message("d", ["a", "b", "c"])
        ]
    table = build_table(messages)
    eq_(4, len(table))
    eq_('b', table["a"].child.message.message_id)
    eq_('c', table["b"].child.message.message_id)
    eq_('d', table["c"].child.message.message_id)
    eq_(None, table["d"].child)

    #
    # Should create valid chain with dummy containers
    # when c is missing
    #
    # a
    # +- b
    #    + - c (dummy)
    #        +- d
    #
    # b
    # +- c (dummy)
    #    +- d
    #
    # c (dummy)
    # +- d
    #
    # d
    messages = [
        make_message("a"),
        make_message("b", ["a"]),
        make_message("d", ["a", "b", "c"])
        ]
    table = build_table(messages)
    eq_(4, len(table))
    eq_('b', table["a"].child.message.message_id)
    eq_(None, table["b"].child.message)
    eq_('d', table["c"].child.message.message_id)
    eq_(None, table["d"].child)

    # processes situations when messages disagree
    # about threading structure
    #
    # a
    # +- b
    #    +- c
    #       +- d
    #
    # a
    # +- c
    #    +- e
    #

    messages = [
        make_message("e", ["a", "c"]),
        make_message("d", ["a", "b", "c"])
        ]
    table = build_table(messages)
    eq_(5, len(table))
    a = table["a"]
    eq_('d', a.child.next.child.message.message_id)
    eq_('e', a.child.next.child.next.message.message_id)

    # processes situations when messages
    # attempt to introduce some loop
    #
    # a
    # +- b
    #    +- c
    #
    # c
    # +- a
    #

    messages = [
        make_message("c", ["a", "b"]),
        make_message("a", ["c"])
        ]
    table = build_table(messages)
    eq_(3, len(table))
    a = table["a"]
    eq_('c', a.child.child.message.message_id)
    c = table["c"]
    eq_(None, c.child)

    # processes situations when we
    # have multiple messages with the same id
    #
    # b
    # +- a
    #
    # c
    # +- a

    messages = [
        make_message("a", ["b"]),
        make_message("a", ["c"])
        ]
    table = build_table(messages)
    eq_(4, len(table))
    eq_('a', table['a'].message.message_id)
    # we have detected conflict and
    # intentionally created fake message it (to avoid loosing message)
    # here it is:
    fake_id = [key for key in table if key not in ('a', 'b', 'c')][0]
    eq_('a', table[fake_id].message.message_id)

@patch.object(MessageId, 'is_valid', Mock(return_value=True))
def test_build_root_set():
    #
    # Should create valid root set
    # in the following order
    #
    # a
    # +- b
    #    + - c
    #        +- d
    #
    # b
    # +- c
    #    +- d
    #
    # c
    # +- d
    #
    # d
    #
    # e (missing)
    # +- f
    #
    # g
    messages = [
        make_message("a"),
        make_message("b", ["a"]),
        make_message("c", ["a", "b"]),
        make_message("d", ["a", "b", "c"]),
        make_message("f", ["e"]),
        make_message("g")
        ]
    table = build_table(messages)
    root = build_root_set(table)
    eq_('g', root.child.message.message_id)
    eq_('f', root.child.next.child.message.message_id)
    eq_('a', root.child.next.next.message.message_id)
    eq_(None, root.child.next.next.next)

    # Thread should became
    #
    # thread
    #   |
    #   +- g
    #   +- f
    #   +- a
    #      +- b
    #         +- c
    #            +- d

    thread = build_thread(messages)
    eq_('g', thread.child.message.message_id)
    eq_('f', thread.child.next.message.message_id)
    eq_('a', thread.child.next.next.message.message_id)
    eq_('b', thread.child.next.next.child.message.message_id)
    eq_('c', thread.child.next.next.child.child.message.message_id)
    eq_('d', thread.child.next.next.child.child.child.message.message_id)


def make_empty(count):
    return [Container() for i in range(count)]

def make_full(*ids):
    return [tc(id) for id in ids]

def tc(*args, **kwargs):
    return Container(wrapper(*args, **kwargs))

def make_message(message_id, references=None, subject=""):
    message = create.text('plain','hey')
    if message_id:
        message.headers['Message-Id'] = '<{0}>'.format(message_id)
    if references:
        message.headers['References'] = ' '.join(
            '<{0}>'.format(rid) for rid in references)
    return message

def wrapper(message_id, references=None, subject=""):
    return Wrapper(make_message(message_id, references, ""))
