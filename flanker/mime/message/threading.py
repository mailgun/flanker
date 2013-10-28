"""
Implements message threading
"""
from email.utils import make_msgid


def build_thread(messages):
    """
    Groups given message list by conversation
    returns tree with root linked to all messages
    """
    thread = build_root_set(
        build_table(messages))
    thread.prune_empty()
    return thread


def build_table(messages):
    id_table = {}
    for message in messages:
        map_message(message, id_table)
    return id_table


def build_root_set(table):
    root = Container()
    for container in table.itervalues():
        if not container.parent:
            root.add_child(container)
    return root


def map_message(message, table):

    def container(message_id):
        return table.setdefault(message_id, Container())

    w = Wrapper(message)
    this = container(w.message_id)

    # process case when we have two messages
    # with the same id, we should put
    # our current message to another container
    # otherwise the message would be lost
    if this.message:
        fake_id = make_msgid()
        this = container(fake_id)
    this.message = w

    # link message parents together
    prev = None
    for parent_id in w.references:
        parent = container(parent_id)
        if prev and not parent.parent and not introduces_loop(prev, parent):
            prev.add_child(parent)
        prev = parent

    # process case where this message has parent
    # unlink the old parent in this case
    if this.parent:
        this.parent.remove_child(this)

    # link to the cool parent instead
    if prev and not introduces_loop(prev, this):
        prev.add_child(this)


def introduces_loop(parent, child):
    return parent == child or child.has_descendant(parent)


class Container(object):
    def __init__(self, message=None):
        self.message = message
        self.parent = None
        self.child = None
        self.next = None
        self.prev = None

    def __str__(self):
        return self.message.message_id if self.message else "dummy"

    @property
    def is_dummy(self):
        return not self.message

    @property
    def in_root_set(self):
        return self.parent.parent is None

    @property
    def has_children(self):
        return self.child is not None

    @property
    def has_one_child(self):
        return self.child and self.child.next is None

    @property
    def last_child(self):
        child = self.child
        while child and child.next:
            child = child.next
        return child

    def iter_children(self):
        child = self.child
        while child:
            yield child
            child = child.next

    def has_descendant(self, container):
        child = self.child
        while child:
            if child == container or child.has_descendant(container):
                return True
            child = child.next
        return False

    def add_child(self, container):
        """
        Inserts child in front of list of children
        """
        if self.child:
            container.next = self.child
            self.child.prev = container

        self.child = container
        self.child.parent = self
        self.child.prev = None

    def remove_child(self, container):
        """
        """
        if container.parent != self:
            raise Exception("Operation on child when I'm not parent!")
        if not container.prev:
            self.child = container.next
            if self.child:
                self.child.prev = None
        else:
            container.prev.next = container.next
            if container.next:
                container.next.prev = container.prev
        container.parent = None
        container.prev = None
        container.next = None

    def replace_with_its_children(self, container):
        """
        Replaces container with its children.
        """
        if not container.has_children:
            return

        for c in container.iter_children():
            c.parent = self

        if not container.prev:
            self.child = container.child
        else:
            container.prev.next = container.child
            container.child.prev = container.prev

        if container.next:
            last_child = container.last_child
            container.next.prev = last_child
            last_child.next = container.next

    def prune_empty(self):
        """
        Removes child containers
        that don't have messages inside.
        """
        container = self.child
        while container:
            if container.is_dummy and not container.has_children:
                next_ = container.next
                self.remove_child(container)
                container = next_
            elif container.is_dummy \
                 and container.has_children \
                 and (not container.in_root_set or container.has_one_child):
                # remove container from the list
                # replacing it with it's children
                next_ = container.child
                self.replace_with_its_children(container)
                container.parent = None
                container.child = None
                container = next_
            elif container.has_children:
                container.prune_empty()
                container = container.next
            else:
                container = container.next


class Wrapper(object):
    def __init__(self, message):
        self.message = message
        self.message_id = message.message_id or make_msgid()
        self.references = message.references
        #self.subject = message.subject
        #self.clean_subject = message.clean_subject
