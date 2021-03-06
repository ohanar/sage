"""
Ordered Rooted Trees

AUTHORS:

- Florent Hivert (2010-2011): initial revision
- Frederic Chapoton (2010): contributed some methods
"""
#*****************************************************************************
#       Copyright (C) 2010 Florent Hivert <Florent.Hivert@univ-rouen.fr>,
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************
from sage.structure.list_clone import ClonableArray, ClonableList
from sage.structure.parent import Parent
from sage.structure.unique_representation import UniqueRepresentation
from sage.misc.classcall_metaclass import ClasscallMetaclass
from sage.misc.lazy_attribute import lazy_class_attribute
from sage.combinat.abstract_tree import (AbstractClonableTree,
                                         AbstractLabelledClonableTree)
from sage.combinat.combinatorial_map import combinatorial_map


class OrderedTree(AbstractClonableTree, ClonableList):
    """
    The class for (ordered rooted) Trees

    An ordered tree is constructed from a node called the root on which one
    has grafted a possibly empty list of trees. There is a total order on the
    children of a node which is given by the order of the elements in the
    list. Note that there is no empty ordered tree.

    INPUT:

    One can create a tree from any list (or more generally iterable) of trees
    or objects convertible to a tree. Alternatively a string is also
    accepted. The syntax is the same as for printing: children are grouped by
    square brackets.

    EXAMPLES::

        sage: x = OrderedTree([])
        sage: x1 = OrderedTree([x,x])
        sage: x2 = OrderedTree([[],[]])
        sage: x1 == x2
        True
        sage: tt1 = OrderedTree([x,x1,x2])
        sage: tt2 = OrderedTree([[], [[], []], x2])
        sage: tt1 == tt2
        True

        sage: OrderedTree([]) == OrderedTree()
        True

    TESTS::

        sage: x1.__hash__() == x2.__hash__()
        True
        sage: tt1.__hash__() == tt2.__hash__()
        True

    Trees are usually immutable. However they inherits from
    :class:`sage.structure.list_clone.ClonableList`. So that they can be
    modified using the clone protocol:

    Trying to modify a non mutable tree raises an error::

        sage: tt1[1] = tt2
        Traceback (most recent call last):
        ...
        ValueError: object is immutable; please change a copy instead.

    Here is the correct way to do it::

        sage: with tt2.clone() as tt2:
        ...    tt2[1] = tt1
        sage: tt2
        [[], [[], [[], []], [[], []]], [[], []]]

    It is also possible to append a child to a tree::

        sage: with tt2.clone() as tt3:
        ...    tt3.append(OrderedTree([]))
        sage: tt3
        [[], [[], [[], []], [[], []]], [[], []], []]

    Or to insert a child in a tree::

        sage: with tt2.clone() as tt3:
        ...    tt3.insert(2, OrderedTree([]))
        sage: tt3
        [[], [[], [[], []], [[], []]], [], [[], []]]

    We check that ``tt1`` is not modified and that everything is correct with
    respect to equality::

        sage: tt1
        [[], [[], []], [[], []]]
        sage: tt1 == tt2
        False
        sage: tt1.__hash__() == tt2.__hash__()
        False

    TESTS::

        sage: tt1bis = OrderedTree(tt1)
        sage: with tt1.clone() as tt1:
        ...    tt1[1] = tt1bis
        sage: tt1
        [[], [[], [[], []], [[], []]], [[], []]]
        sage: tt1 == tt2
        True
        sage: tt1.__hash__() == tt2.__hash__()
        True
        sage: len(tt1)
        3
        sage: tt1[2]
        [[], []]
        sage: tt1[3]
        Traceback (most recent call last):
        ...
        IndexError: list index out of range
        sage: tt1[1:2]
        [[[], [[], []], [[], []]]]

    Various tests involving construction, equality and hashing::

        sage: OrderedTree() == OrderedTree()
        True
        sage: t1 = OrderedTree([[],[[]]])
        sage: t2 = OrderedTree([[],[[]]])
        sage: t1 == t2
        True
        sage: t2 = OrderedTree(t1)
        sage: t1 == t2
        True
        sage: t1 = OrderedTree([[],[[]]])
        sage: t2 = OrderedTree([[[]],[]])
        sage: t1 == t2
        False

        sage: t1 = OrderedTree([[],[[]]])
        sage: t2 = OrderedTree([[],[[]]])
        sage: t1.__hash__() == t2.__hash__()
        True
        sage: t2 = OrderedTree([[[]],[]])
        sage: t1.__hash__() == t2.__hash__()
        False
        sage: OrderedTree().__hash__() == OrderedTree([]).__hash__()
        True
        sage: tt1 = OrderedTree([t1,t2,t1])
        sage: tt2 = OrderedTree([t1, [[[]],[]], t1])
        sage: tt1.__hash__() == tt2.__hash__()
        True

    Check that the hash value is correctly updated after modification::

        sage: with tt2.clone() as tt2:
        ...    tt2[1,1] = tt1
        sage: tt1.__hash__() == tt2.__hash__()
        False
    """

    __metaclass__ = ClasscallMetaclass

    @staticmethod
    def __classcall_private__(cls, *args, **opts):
        """
        Ensure that trees created by the enumerated sets and directly
        are the same and that they are instances of :class:`OrderedTree`

        TESTS::

            sage: issubclass(OrderedTrees().element_class, OrderedTree)
            True
            sage: t0 = OrderedTree([[],[[], []]])
            sage: t0.parent()
            Ordered trees
            sage: type(t0)
            <class 'sage.combinat.ordered_tree.OrderedTrees_all_with_category.element_class'>

            sage: t1 = OrderedTrees()([[],[[], []]])
            sage: t1.parent() is t0.parent()
            True
            sage: type(t1) is type(t0)
            True

            sage: t1 = OrderedTrees(4)([[],[[]]])
            sage: t1.parent() is t0.parent()
            True
            sage: type(t1) is type(t0)
            True
        """
        return cls._auto_parent.element_class(cls._auto_parent, *args, **opts)

    @lazy_class_attribute
    def _auto_parent(cls):
        """
        The automatic parent of the element of this class

        When calling the constructor of an element of this class, one needs a
        parent. This class attribute specifies which parent is used.

        EXAMPLES::

            sage: OrderedTree([[],[[]]])._auto_parent
            Ordered trees
            sage: OrderedTree([[],[[]]]).parent()
            Ordered trees

        .. NOTE::

            It is possible to bypass the automatic parent mechanism using:

                sage: t1 = OrderedTree.__new__(OrderedTree, Parent(), [])
                sage: t1.__init__(Parent(), [])
                sage: t1
                []
                sage: t1.parent()
                <type 'sage.structure.parent.Parent'>
        """
        return OrderedTrees_all()

    def __init__(self, parent=None, children=[], check=True):
        """
        TESTS::

            sage: t1 = OrderedTrees(4)([[],[[]]])
            sage: TestSuite(t1).run()
            sage: OrderedTrees()("[]") # indirect doctest
            []
            sage: all(OrderedTree(repr(tr)) == tr for i in range(6) for tr in OrderedTrees(i))
            True
        """
        if type(children) is str:
            children = eval(children)
        if (children.__class__ is self.__class__ and
            children.parent() == parent):
            children = list(children)
        else:
            children = [self.__class__(parent, x) for x in children]
        ClonableArray.__init__(self, parent, children, check=check)

    def is_empty(self):
        """
        Return if ``self`` is the empty tree

        For ordered trees, returns always ``False``

        .. NOTE:: this is different from ``bool(t)`` which returns whether
                  ``t`` has some child or not.

        EXAMPLES::

            sage: t = OrderedTrees(4)([[],[[]]])
            sage: t.is_empty()
            False
            sage: bool(t)
            True
        """
        return False

    def _to_binary_tree_rec(self, bijection="left"):
        r"""
        Internal recursive method to obtain a binary tree from an ordered
        tree.

        EXAMPLES::

            sage: T = OrderedTree([[],[]])
            sage: T._to_binary_tree_rec()
            [[., .], .]
            sage: T._to_binary_tree_rec(bijection="right")
            [., [., .]]
            sage: T = OrderedTree([[], [[], []], [[], [[]]]])
            sage: T._to_binary_tree_rec()
            [[[., .], [[., .], .]], [[., .], [., .]]]
            sage: T._to_binary_tree_rec(bijection="right")
            [., [[., [., .]], [[., [[., .], .]], .]]]
        """
        from sage.combinat.binary_tree import BinaryTree
        root = BinaryTree()
        if(bijection=="left"):
            for child in self:
                root = BinaryTree([root,child._to_binary_tree_rec(bijection)])
        elif(bijection=="right"):
            children = list(self)
            children.reverse()
            for child in children:
                root = BinaryTree([child._to_binary_tree_rec(bijection),root])
        else:
            raise ValueError("the bijection argument should be either left or right")
        return root

    @combinatorial_map(name="To binary tree, left brother = left child")
    def to_binary_tree_left_branch(self):
        r"""
        Return a binary tree of size `n-1` by the following recursive rule:

        - if `x` is the left brother of `y`, `x` becomes the left child
          of `y`
        - if `x` is the last child of `y`, `x` becomes the right child
          of `y`

        EXAMPLES::

            sage: T = OrderedTree([[],[]])
            sage: T.to_binary_tree_left_branch()
            [[., .], .]
            sage: T = OrderedTree([[], [[], []], [[], [[]]]])
            sage: T.to_binary_tree_left_branch()
            [[[., .], [[., .], .]], [[., .], [., .]]]

        TESTS::

            sage: T = OrderedTree([[],[]])
            sage: T == T.to_binary_tree_left_branch().to_ordered_tree_left_branch()
            True
            sage: T = OrderedTree([[], [[], []], [[], [[]]]])
            sage: T == T.to_binary_tree_left_branch().to_ordered_tree_left_branch()
            True
        """
        return self._to_binary_tree_rec()

    @combinatorial_map(name="To binary tree, right brother = right child")
    def to_binary_tree_right_branch(self):
        r"""
        Return a binary tree of size n-1 by the following recursive rule:

        - if `x` is the right brother of `y`, `x` becomes the right child
          of `y`
        - if `x` is the first child of `y`, `x` becomes the left child
          of `y`

        EXAMPLES::

            sage: T = OrderedTree([[],[]])
            sage: T.to_binary_tree_right_branch()
            [., [., .]]
            sage: T = OrderedTree([[], [[], []], [[], [[]]]])
            sage: T.to_binary_tree_right_branch()
            [., [[., [., .]], [[., [[., .], .]], .]]]

        TESTS::

            sage: T = OrderedTree([[],[]])
            sage: T == T.to_binary_tree_right_branch().to_ordered_tree_right_branch()
            True
            sage: T = OrderedTree([[], [[], []], [[], [[]]]])
            sage: T == T.to_binary_tree_right_branch().to_ordered_tree_right_branch()
            True
        """
        return self._to_binary_tree_rec(bijection="right")

    @combinatorial_map(name="To Dyck path")
    def to_dyck_word(self):
        r"""
        Return the dyck path corresponding to ``self`` where the maximal
        height of the Dyck path is the depth of ``self`` .

        EXAMPLES::

            sage: T = OrderedTree([[],[]])
            sage: T.to_dyck_word()
            [1, 0, 1, 0]
            sage: T = OrderedTree([[],[[]]])
            sage: T.to_dyck_word()
            [1, 0, 1, 1, 0, 0]
            sage: T = OrderedTree([[], [[], []], [[], [[]]]])
            sage: T.to_dyck_word()
            [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0]
        """
        word = []
        for child in self:
            word.append(1)
            word.extend(child.to_dyck_word())
            word.append(0)
        from sage.combinat.dyck_word import DyckWord
        return DyckWord(word)

    @combinatorial_map(order=2,name="Left-right symmetry")
    def left_right_symmetry(self):
        r"""
        Return the symmetric tree of ``self``

        EXAMPLES::

            sage: T = OrderedTree([[],[[]]])
            sage: T.left_right_symmetry()
            [[[]], []]
            sage: T = OrderedTree([[], [[], []], [[], [[]]]])
            sage: T.left_right_symmetry()
            [[[[]], []], [[], []], []]
        """
        children = [c.left_right_symmetry() for c in self]
        children.reverse()
        return OrderedTree(children)

from sage.categories.sets_cat import Sets, EmptySetError
from sage.rings.integer import Integer
from sage.sets.non_negative_integers import NonNegativeIntegers
from sage.sets.disjoint_union_enumerated_sets import DisjointUnionEnumeratedSets
from sage.sets.family import Family
from sage.misc.cachefunc import cached_method

# Abstract class to serve as a Factory no instance are created.
class OrderedTrees(UniqueRepresentation, Parent):
    """
    Factory for ordered trees

    INPUT:

    - ``size`` -- (optional) an integer

    OUPUT:

    - the set of all ordered trees (of the given ``size`` if specified)

    EXAMPLES::

        sage: OrderedTrees()
        Ordered trees

        sage: OrderedTrees(2)
        Ordered trees of size 2

    .. NOTE:: this is a factory class whose constructor returns instances of
              subclasses.

    .. NOTE:: the fact that OrderedTrees is a class instead of a simple callable
              is an implementation detail. It could be changed in the future
              and one should not rely on it.
    """
    @staticmethod
    def __classcall_private__(cls, n=None):
        """
        TESTS::

            sage: from sage.combinat.ordered_tree import OrderedTrees_all, OrderedTrees_size
            sage: isinstance(OrderedTrees(2), OrderedTrees)
            True
            sage: isinstance(OrderedTrees(), OrderedTrees)
            True
            sage: OrderedTrees(2) is OrderedTrees_size(2)
            True
            sage: OrderedTrees(5).cardinality()
            14
            sage: OrderedTrees() is OrderedTrees_all()
            True
        """
        if n is None:
            return OrderedTrees_all()
        else:
            if not (isinstance(n, (Integer, int)) and n >= 0):
                raise ValueError("n must be a non negative integer")
            return OrderedTrees_size(Integer(n))

    @cached_method
    def leaf(self):
        """
        Return a leaf tree with ``self`` as parent

        EXAMPLES::

            sage: OrderedTrees().leaf()
            []

        TEST::

            sage: (OrderedTrees().leaf() is
            ...    sage.combinat.ordered_tree.OrderedTrees_all().leaf())
            True
        """
        return self([])

class OrderedTrees_all(DisjointUnionEnumeratedSets, OrderedTrees):
    """
    The set of all ordered trees

    EXAMPLES::

        sage: OT = OrderedTrees(); OT
        Ordered trees
        sage: OT.cardinality()
        +Infinity
    """

    def __init__(self):
        """
        TESTS::

            sage: from sage.combinat.ordered_tree import OrderedTrees_all
            sage: B = OrderedTrees_all()
            sage: B.cardinality()
            +Infinity

            sage: it = iter(B)
            sage: (it.next(), it.next(), it.next(), it.next(), it.next())
            ([], [[]], [[], []], [[[]]], [[], [], []])
            sage: it.next().parent()
            Ordered trees
            sage: B([])
            []

            sage: B is OrderedTrees_all()
            True
            sage: TestSuite(B).run()
            """
        DisjointUnionEnumeratedSets.__init__(
            self, Family(NonNegativeIntegers(), OrderedTrees_size),
            facade=True, keepkey=False)

    def _repr_(self):
        """
        TEST::

            sage: OrderedTrees()   # indirect doctest
            Ordered trees
        """
        return "Ordered trees"

    def __contains__(self, x):
        """
        TESTS::

            sage: T = OrderedTrees()
            sage: 1 in T
            False
            sage: T([]) in T
            True
        """
        return isinstance(x, self.element_class)

    def unlabelled_trees(self):
        """
        Return the set of unlabelled trees associated to ``self``

        EXAMPLES::

            sage: OrderedTrees().unlabelled_trees()
            Ordered trees
        """
        return self

    def labelled_trees(self):
        """
        Return the set of unlabelled trees associated to ``self``

        EXAMPLES::

            sage: OrderedTrees().labelled_trees()
            Labelled ordered trees
        """
        return LabelledOrderedTrees()

    def _element_constructor_(self, *args, **keywords):
        """
        EXAMPLES::

            sage: T = OrderedTrees()
            sage: T([])     # indirect doctest
            []
        """
        return self.element_class(self, *args, **keywords)

    Element = OrderedTree



from sage.misc.lazy_attribute import lazy_attribute
from sage.categories.finite_enumerated_sets import FiniteEnumeratedSets
from combinat import catalan_number
from sage.combinat.composition import Compositions
from sage.combinat.cartesian_product import CartesianProduct
#################################################################
# Enumerated set of binary trees of a given size
#################################################################
class OrderedTrees_size(OrderedTrees):
    """
    The enumerated sets of binary trees of a given size

    EXAMPLES::

        sage: S = OrderedTrees(3); S
        Ordered trees of size 3
        sage: S.cardinality()
        2
        sage: S.list()
        [[[], []], [[[]]]]
    """
    def __init__(self, size):
        """
        TESTS::

            sage: from sage.combinat.ordered_tree import OrderedTrees_size
            sage: TestSuite(OrderedTrees_size(0)).run()
            sage: for i in range(6): TestSuite(OrderedTrees_size(i)).run()
        """
        super(OrderedTrees_size, self).__init__(category = FiniteEnumeratedSets())
        self._size = size

    def _repr_(self):
        """
        TESTS::

            sage: OrderedTrees(3)   # indirect doctest
            Ordered trees of size 3
        """
        return "Ordered trees of size %s"%(self._size)

    def __contains__(self, x):
        """
        TESTS::

            sage: T = OrderedTrees(3)
            sage: 1 in T
            False
            sage: T([[],[]]) in T
            True
        """
        return isinstance(x, self.element_class) and x.node_number() == self._size

    def _an_element_(self):
        """
        TESTS::

            sage: OrderedTrees(3).an_element()   # indirect doctest
            [[], []]
        """
        if self._size == 0:
            raise EmptySetError
        return self.first()

    def cardinality(self):
        """
        The cardinality of ``self``

        This is a Catalan number

        TESTS::

            sage: OrderedTrees(0).cardinality()
            0
            sage: OrderedTrees(1).cardinality()
            1
            sage: OrderedTrees(6).cardinality()
            42
        """
        if self._size == 0:
            return Integer(0)
        else:
            return catalan_number(self._size-1)

    def __iter__(self):
        """
        A basic generator

        .. TODO:: could be optimized.

        TESTS::

            sage: OrderedTrees(0).list()
            []
            sage: OrderedTrees(1).list()
            [[]]
            sage: OrderedTrees(2).list()
            [[[]]]
            sage: OrderedTrees(3).list()
            [[[], []], [[[]]]]
            sage: OrderedTrees(4).list()
            [[[], [], []], [[], [[]]], [[[]], []], [[[], []]], [[[[]]]]]
        """
        if self._size == 0:
            return
        else:
            for c in Compositions(self._size-1):
                for lst in CartesianProduct(*(map(self.__class__, c))):
                    yield self._element_constructor_(lst)

    @lazy_attribute
    def _parent_for(self):
        """
        Return the parent of the element generated by ``self``

        TESTS::

            sage: OrderedTrees(3)._parent_for
            Ordered trees
        """
        return OrderedTrees_all()

    @lazy_attribute
    def element_class(self):
        """
        The class of the element of ``self``

        EXAMPLES::

            sage: from sage.combinat.ordered_tree import OrderedTrees_size, OrderedTrees_all
            sage: S = OrderedTrees_size(3)
            sage: S.element_class is OrderedTrees().element_class
            True
            sage: S.first().__class__ == OrderedTrees_all().first().__class__
            True
        """
        return self._parent_for.element_class

    def _element_constructor_(self, *args, **keywords):
        """
        EXAMPLES::

            sage: S = OrderedTrees(0)
            sage: S([])   # indirect doctest
            Traceback (most recent call last):
            ...
            ValueError: wrong number of nodes

            sage: S = OrderedTrees(1)   # indirect doctest
            sage: S([])
            []
        """
        res = self.element_class(self._parent_for, *args, **keywords)
        if res.node_number() != self._size:
            raise ValueError("wrong number of nodes")
        return res


class LabelledOrderedTree(AbstractLabelledClonableTree, OrderedTree):
    """
    Labelled ordered trees

    A labelled ordered tree is an ordered tree with a label attached at each
    node.

    INPUT:

    - ``children`` -- a list or tuple or more generally any iterable
                      of trees or object convertible to trees
    - ``label`` -- any Sage object default to ``None``

    EXAMPLES::

        sage: x = LabelledOrderedTree([], label = 3); x
        3[]
        sage: LabelledOrderedTree([x, x, x], label = 2)
        2[3[], 3[], 3[]]
        sage: LabelledOrderedTree((x, x, x), label = 2)
        2[3[], 3[], 3[]]
        sage: LabelledOrderedTree([[],[[], []]], label = 3)
        3[None[], None[None[], None[]]]
    """
    __metaclass__ = ClasscallMetaclass

    @staticmethod
    def __classcall_private__(cls, *args, **opts):
        """
        Ensure that trees created by the sets and directly are the same and
        that they are instances of :class:`LabelledOrderedTree`

        TESTS::

            sage: issubclass(LabelledOrderedTrees().element_class, LabelledOrderedTree)
            True
            sage: t0 = LabelledOrderedTree([[],[[], []]], label = 3)
            sage: t0.parent()
            Labelled ordered trees
            sage: type(t0)
            <class 'sage.combinat.ordered_tree.LabelledOrderedTrees_with_category.element_class'>
        """
        return cls._auto_parent.element_class(cls._auto_parent, *args, **opts)

    @lazy_class_attribute
    def _auto_parent(cls):
        """
        The automatic parent of the element of this class

        When calling the constructor of an element of this class, one needs a
        parent. This class attribute specifies which parent is used.

        EXAMPLES::

            sage: LabelledOrderedTree._auto_parent
            Labelled ordered trees
            sage: LabelledOrderedTree([], label = 3).parent()
            Labelled ordered trees
         """
        return LabelledOrderedTrees()

    _UnLabelled = OrderedTree


from sage.rings.infinity import Infinity
class LabelledOrderedTrees(UniqueRepresentation, Parent):
    """
    This is a parent stub to serve as a factory class for trees with various
    labels constraints

    EXAMPLES::

        sage: LOT = LabelledOrderedTrees(); LOT
        Labelled ordered trees
        sage: x = LOT([], label = 3); x
        3[]
        sage: x.parent() is LOT
        True
        sage: y = LOT([x, x, x], label = 2); y
        2[3[], 3[], 3[]]
        sage: y.parent() is LOT
        True
    """
    def __init__(self, category=None):
        """
        TESTS::

            sage: TestSuite(LabelledOrderedTrees()).run()
        """
        if category is None:
            category = Sets()
        Parent.__init__(self, category = category)

    def _repr_(self):
        """
        TESTS::

            sage: LabelledOrderedTrees()   # indirect doctest
            Labelled ordered trees
        """
        return "Labelled ordered trees"

    def cardinality(self):
        """
        Return the cardinality of `self`

        EXAMPLE::

            sage: LabelledOrderedTrees().cardinality()
            +Infinity
        """
        return Infinity

    def _an_element_(self):
        """
        Return a labelled tree

        EXAMPLE::

            sage: LabelledOrderedTrees().an_element()   # indirect doctest
            toto[3[], 42[3[], 3[]], 5[None[]]]
        """
        LT = self._element_constructor_
        t  = LT([], label = 3)
        t1 = LT([t,t], label = 42)
        t2  = LT([[]], label = 5)
        return LT([t,t1,t2], label = "toto")

    def _element_constructor_(self, *args, **keywords):
        """
        EXAMPLES::

            sage: T = LabelledOrderedTrees()
            sage: T([], label=2)     # indirect doctest
            2[]
        """
        return self.element_class(self, *args, **keywords)

    def unlabelled_trees(self):
        """
        Return the set of unlabelled trees associated to ``self``

        EXAMPLES::

            sage: LabelledOrderedTrees().unlabelled_trees()
            Ordered trees
        """
        return OrderedTrees_all()

    def labelled_trees(self):
        """
        Return the set of labelled trees associated to ``self``

        EXAMPLES::

            sage: LabelledOrderedTrees().labelled_trees()
            Labelled ordered trees
            sage: LOT = LabelledOrderedTrees()
            sage: x = LOT([], label = 3)
            sage: y = LOT([x, x, x], label = 2)
            sage: y.canonical_labelling()
            1[2[], 3[], 4[]]
        """
        return self

    Element = LabelledOrderedTree
