r"""
Littelmann paths

AUTHORS:

- Mark Shimozono, Anne Schilling (2012): Initial version
- Anne Schilling (2013): Implemented :class:`CrystalOfProjectedLevelZeroLSPaths`
"""
#****************************************************************************
#       Copyright (C) 2012 Mark Shimozono
#                          Anne Schilling
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
#****************************************************************************

from sage.misc.cachefunc import cached_in_parent_method
from sage.structure.unique_representation import UniqueRepresentation
from sage.structure.element_wrapper import ElementWrapper
from sage.structure.parent import Parent
from sage.categories.crystals import Crystals
from sage.categories.highest_weight_crystals import HighestWeightCrystals
from sage.categories.regular_crystals import RegularCrystals
from sage.categories.finite_crystals import FiniteCrystals
from sage.categories.classical_crystals import ClassicalCrystals
from sage.categories.infinite_enumerated_sets import InfiniteEnumeratedSets
from sage.combinat.root_system.cartan_type import CartanType
from sage.combinat.root_system.weyl_group import WeylGroup
from sage.rings.integer import Integer
from sage.rings.rational_field import QQ
from sage.combinat.root_system.root_system import RootSystem
from sage.functions.other import floor
from sage.misc.latex import latex


class CrystalOfLSPaths(UniqueRepresentation, Parent):
    r"""
    Crystal graph of LS paths generated from the straight-line path to a given weight.

    INPUT:

    - ``cartan_type`` -- (optional) the Cartan type of a finite or affine root system
    - ``starting_weight`` -- a weight; if ``cartan_type`` is given, then the weight should
      be given as a list of coefficients of the fundamental weights, otherwise it should
      be given in the ``weight_space`` basis; for affine highest weight crystals, one needs
      to use the extended weight space.

    The crystal class of piecewise linear paths in the weight space,
    generated from a straight-line path from the origin to a given
    element of the weight lattice.

    OUTPUT:

    - a tuple of weights defining the directions of the piecewise linear segments

    EXAMPLES::

        sage: R = RootSystem(['A',2,1])
        sage: La = R.weight_space(extended = True).basis()
        sage: B = CrystalOfLSPaths(La[2]-La[0]); B
        The crystal of LS paths of type ['A', 2, 1] and weight -Lambda[0] + Lambda[2]

        sage: C = CrystalOfLSPaths(['A',2,1],[-1,0,1]); C
        The crystal of LS paths of type ['A', 2, 1] and weight -Lambda[0] + Lambda[2]
        sage: B == C
        True
        sage: c = C.module_generators[0]; c
        (-Lambda[0] + Lambda[2],)
        sage: [c.f(i) for i in C.index_set()]
        [None, None, (Lambda[1] - Lambda[2],)]

        sage: R = C.R; R
        Root system of type ['A', 2, 1]
        sage: Lambda = R.weight_space().basis(); Lambda
        Finite family {0: Lambda[0], 1: Lambda[1], 2: Lambda[2]}
        sage: b=C(tuple([-Lambda[0]+Lambda[2]]))
        sage: b==c
        True
        sage: b.f(2)
        (Lambda[1] - Lambda[2],)

    For classical highest weight crystals we can also compare the results with the tableaux implementation::

        sage: C = CrystalOfLSPaths(['A',2],[1,1])
        sage: list(set(C.list()))
        [(-Lambda[1] - Lambda[2],), (-Lambda[1] + 1/2*Lambda[2], Lambda[1] - 1/2*Lambda[2]), (-Lambda[1] + 2*Lambda[2],),
        (1/2*Lambda[1] - Lambda[2], -1/2*Lambda[1] + Lambda[2]), (Lambda[1] - 2*Lambda[2],), (-2*Lambda[1] + Lambda[2],),
        (2*Lambda[1] - Lambda[2],), (Lambda[1] + Lambda[2],)]
        sage: C.cardinality()
        8
        sage: B = CrystalOfTableaux(['A',2],shape=[2,1])
        sage: B.cardinality()
        8
        sage: B.digraph().is_isomorphic(C.digraph())
        True

    Make sure you use the weight space and not the weight lattice for your weights::

        sage: R = RootSystem(['A',2,1])
        sage: La = R.weight_lattice(extended = True).basis()
        sage: B = CrystalOfLSPaths(La[2]); B
        Traceback (most recent call last):
        ...
        ValueError: Please use the weight space, rather than weight lattice for your weights

    REFERENCES:

    .. [Littelmann95] P. Littelmann, Paths and root operators in representation
       theory. Ann. of Math. (2) 142 (1995), no. 3, 499-525.
    """

    @staticmethod
    def __classcall_private__(cls, starting_weight, cartan_type = None):
        """
        Classcall to mend the input.

        Internally, the CrystalOfLSPaths code works with a ``starting_weight`` that
        is in the ``weight_space`` associated to the crystal. The user can, however,
        also input a ``cartan_type`` and the coefficients of the fundamental weights
        as ``starting_weight``. This code transforms the input into the right
        format (also necessary for UniqueRepresentation).

        TESTS::

            sage: CrystalOfLSPaths(['A',2,1],[-1,0,1])
            The crystal of LS paths of type ['A', 2, 1] and weight -Lambda[0] + Lambda[2]

            sage: R = RootSystem(['B',2,1])
            sage: La = R.weight_space().basis()
            sage: C = CrystalOfLSPaths(['B',2,1],[0,0,1])
            sage: B = CrystalOfLSPaths(La[2])
            sage: B is C
            True
        """
        if cartan_type is not None:
            cartan_type, starting_weight = CartanType(starting_weight), cartan_type
            if cartan_type.is_affine():
                extended = True
            else:
                extended = False

            R = RootSystem(cartan_type)
            P = R.weight_space(extended = extended)
            Lambda = P.basis()
            offset = R.index_set()[Integer(0)]
            starting_weight = P.sum(starting_weight[j-offset]*Lambda[j] for j in R.index_set())

        return super(CrystalOfLSPaths, cls).__classcall__(cls, starting_weight)

    def __init__(self, starting_weight):
        """
        EXAMPLES::

            sage: C = CrystalOfLSPaths(['A',2,1],[-1,0,1]); C
            The crystal of LS paths of type ['A', 2, 1] and weight -Lambda[0] + Lambda[2]
            sage: C.R
            Root system of type ['A', 2, 1]
            sage: C.weight
            -Lambda[0] + Lambda[2]
            sage: C.weight.parent()
            Extended weight space over the Rational Field of the Root system of type ['A', 2, 1]
            sage: C.module_generators
            [(-Lambda[0] + Lambda[2],)]

        TESTS::

            sage: C = CrystalOfLSPaths(['A',2,1], [-1,0,1])
            sage: TestSuite(C).run()
            sage: C = CrystalOfLSPaths(['E',6], [1,0,0,0,0,0])
            sage: TestSuite(C).run()
        """
        cartan_type = starting_weight.parent().cartan_type()
        self.R = RootSystem(cartan_type)
        self.weight = starting_weight
        if not self.weight.parent().base_ring().has_coerce_map_from(QQ):
             raise ValueError, "Please use the weight space, rather than weight lattice for your weights"
        self._cartan_type = cartan_type
        self._name = "The crystal of LS paths of type %s and weight %s"%(cartan_type,starting_weight)
        if cartan_type.is_affine():
            if all(i>=0 for i in starting_weight.coefficients()):
                Parent.__init__( self, category = (RegularCrystals(),
                                                   HighestWeightCrystals(),
                                                   InfiniteEnumeratedSets()) )
            elif starting_weight.parent().is_extended():
                Parent.__init__(self, category = (RegularCrystals(), InfiniteEnumeratedSets()))
            else:
                Parent.__init__(self, category = (RegularCrystals(), FiniteCrystals()))
        else:
            Parent.__init__(self, category = ClassicalCrystals())

        if starting_weight == starting_weight.parent().zero():
            initial_element = self(tuple([]))
        else:
            initial_element = self(tuple([starting_weight]))
        self.module_generators = [initial_element]

    def _repr_(self):
        """
        EXAMPLES::

            sage: CrystalOfLSPaths(['B',3],[1,1,0]) # indirect doctest
            The crystal of LS paths of type ['B', 3] and weight Lambda[1] + Lambda[2]
        """
        return self._name

    class Element(ElementWrapper):
        """
        TESTS::

            sage: C = CrystalOfLSPaths(['E',6],[1,0,0,0,0,0])
            sage: c=C.an_element()
            sage: TestSuite(c).run()
        """

        def endpoint(self):
            r"""
            Computes the endpoint of the path.

            EXAMPLES::

                sage: C = CrystalOfLSPaths(['A',2],[1,1])
                sage: b = C.module_generators[0]
                sage: b.endpoint()
                Lambda[1] + Lambda[2]
                sage: b.f_string([1,2,2,1])
                (-Lambda[1] - Lambda[2],)
                sage: b.f_string([1,2,2,1]).endpoint()
                -Lambda[1] - Lambda[2]
                sage: b.f_string([1,2])
                (1/2*Lambda[1] - Lambda[2], -1/2*Lambda[1] + Lambda[2])
                sage: b.f_string([1,2]).endpoint()
                0
                sage: b = C([])
                sage: b.endpoint()
                0
            """
            if len(self.value) > 0:
                return sum(self.value)
            return self.parent().weight.parent().zero()
            #return self.parent().R.weight_space(extended = self.parent().extended).zero()

        def compress(self):
            r"""
            Merges consecutive positively parallel steps present in the path.

            EXAMPLES::

                sage: C = CrystalOfLSPaths(['A',2],[1,1])
                sage: Lambda = C.R.weight_space().fundamental_weights(); Lambda
                Finite family {1: Lambda[1], 2: Lambda[2]}
                sage: c = C(tuple([1/2*Lambda[1]+1/2*Lambda[2], 1/2*Lambda[1]+1/2*Lambda[2]]))
                sage: c.compress()
                (Lambda[1] + Lambda[2],)
            """
            def positively_parallel_weights(v, w):
                """
                Checks whether the vectors ``v`` and ``w`` are positive scalar multiples of each other.
                """
                supp = v.support()
                if len(supp) > 0:
                    i = supp[0]
                    if v[i]*w[i] > 0 and v[i]*w == w[i]*v:
                        return True
                return False

            if len(self.value) == 0:
                return self
            q = []
            curr = self.value[0]
            for i in range(1,len(self.value)):
                if positively_parallel_weights(curr,self.value[i]):
                    curr = curr + self.value[i]
                else:
                    q.append(curr)
                    curr = self.value[i]
            q.append(curr)
            return self.parent()(tuple(q))

        def split_step(self, which_step, r):
            r"""
            Splits indicated step into two parallel steps of relative lengths `r` and `1-r`.

            INPUT:

            - ``which_step`` -- a position in the tuple ``self``
            - ``r`` -- a rational number between 0 and 1

            EXAMPLES::

                sage: C = CrystalOfLSPaths(['A',2],[1,1])
                sage: b = C.module_generators[0]
                sage: b.split_step(0,1/3)
                (1/3*Lambda[1] + 1/3*Lambda[2], 2/3*Lambda[1] + 2/3*Lambda[2])
            """
            assert which_step in range(len(self.value))
            v = self.value[which_step]
            return self.parent()(self.value[:which_step]+tuple([r*v,(1-r)*v])+self.value[which_step+1:])

        def reflect_step(self, which_step, i):
            r"""
            Apply the `i`-th simple reflection to the indicated step in ``self``.

            EXAMPLES::

                sage: C = CrystalOfLSPaths(['A',2],[1,1])
                sage: b = C.module_generators[0]
                sage: b.reflect_step(0,1)
                (-Lambda[1] + 2*Lambda[2],)
                sage: b.reflect_step(0,2)
                (2*Lambda[1] - Lambda[2],)
            """
            assert i in self.index_set()
            assert which_step in range(len(self.value))
            return self.parent()(self.value[:which_step]+tuple([self.value[which_step].simple_reflection(i)])+self.value[which_step+1:])

        def _string_data(self, i):
            r"""
            Computes the `i`-string data of ``self``.

            TESTS::

                sage: C = CrystalOfLSPaths(['A',2],[1,1])
                sage: b = C.module_generators[0]
                sage: b._string_data(1)
                ()
                sage: b._string_data(2)
                ()
                sage: b.f(1)._string_data(1)
                ((0, -1, -1),)
                sage: b.f(1).f(2)._string_data(2)
                ((0, -1, -1),)
            """
            if len(self.value) == 0:
                return ()
            # get the i-th simple coroot
            alv = self.value[0].parent().alphacheck()[i]
            # Compute the i-heights of the steps of vs
            steps = [v.scalar(alv) for v in self.value]
            # Get the wet step data
            minima_pos = []
            ps = 0
            psmin = 0
            for ix in range(len(steps)):
                ps = ps + steps[ix]
                if ps < psmin:
                    minima_pos.append((ix,ps,steps[ix]))
                    psmin = ps
            return tuple(minima_pos)

        def epsilon(self, i):
            r"""
            Returns the distance to the beginning of the `i`-string.

            This method overrides the generic implementation in the category of crystals
            since this computation is more efficient.

            EXAMPLES::

                sage: C = CrystalOfLSPaths(['A',2],[1,1])
                sage: [c.epsilon(1) for c in C]
                [0, 1, 0, 0, 1, 0, 1, 2]
                sage: [c.epsilon(2) for c in C]
                [0, 0, 1, 2, 1, 1, 0, 0]
            """
            return self.e(i,length_only=True)

        def phi(self, i):
            r"""
            Returns the distance to the end of the `i`-string.

            This method overrides the generic implementation in the category of crystals
            since this computation is more efficient.

            EXAMPLES::

                sage: C = CrystalOfLSPaths(['A',2],[1,1])
                sage: [c.phi(1) for c in C]
                [1, 0, 0, 1, 0, 2, 1, 0]
                sage: [c.phi(2) for c in C]
                [1, 2, 1, 0, 0, 0, 0, 1]
            """
            return self.f(i,length_only=True)

        def e(self, i, power=1, to_string_end=False, length_only=False):
            r"""
            Returns the `i`-th crystal raising operator on ``self``.

            INPUT:

            - ``i`` -- element of the index set of the underlying root system
            - ``power`` -- positive integer; specifies the power of the raising operator
              to be applied (default: 1)
            - ``to_string_end`` -- boolean; if set to True, returns the dominant end of the
              `i`-string of ``self``. (default: False)
            - ``length_only`` -- boolean; if set to True, returns the distance to the dominant
              end of the `i`-string of ``self``.

            EXAMPLES::

                sage: C = CrystalOfLSPaths(['A',2],[1,1])
                sage: c = C[2]; c
                (1/2*Lambda[1] - Lambda[2], -1/2*Lambda[1] + Lambda[2])
                sage: c.e(1)
                sage: c.e(2)
                (-Lambda[1] + 2*Lambda[2],)
                sage: c.e(2,to_string_end=True)
                (-Lambda[1] + 2*Lambda[2],)
                sage: c.e(1,to_string_end=True)
                (1/2*Lambda[1] - Lambda[2], -1/2*Lambda[1] + Lambda[2])
                sage: c.e(1,length_only=True)
                0
            """
            assert i in self.index_set()
            data = self._string_data(i)
            # compute the minimum i-height M on the path
            if len(data) == 0:
                M = 0
            else:
                M = data[-1][1]
            max_raisings = floor(-M)
            if length_only:
                return max_raisings
            # set the power of e_i to apply
            if to_string_end:
                p = max_raisings
            else:
                p = power
            if p > max_raisings:
                return None

            # copy the vector sequence into a working vector sequence ws
            #!!! ws only needs to be the actual vector sequence, not some
            #!!! fancy crystal graph element
            ws = self.parent()(self.value)

            ix = len(data)-1
            while ix >= 0 and data[ix][1] < M + p:
            # get the index of the current step to be processed
                j = data[ix][0]
                # find the i-height where the current step might need to be split
                if ix == 0:
                    prev_ht = M + p
                else:
                    prev_ht = min(data[ix-1][1],M+p)
                # if necessary split the step. Then reflect the wet part.
                if data[ix][1] - data[ix][2] > prev_ht:
                    ws = ws.split_step(j,1-(prev_ht-data[ix][1])/(-data[ix][2]))
                    ws = ws.reflect_step(j+1,i)
                else:
                    ws = ws.reflect_step(j,i)
                ix = ix - 1
            #!!! at this point we should return the fancy crystal graph element
            #!!! corresponding to the humble vector sequence ws
            return self.parent()(ws.compress())

        def dualize(self):
            r"""
            Returns dualized path.

            EXAMPLES::

                sage: C = CrystalOfLSPaths(['A',2],[1,1])
                sage: for c in C:
                ...     print c, c.dualize()
                ...
                (Lambda[1] + Lambda[2],) (-Lambda[1] - Lambda[2],)
                (-Lambda[1] + 2*Lambda[2],) (Lambda[1] - 2*Lambda[2],)
                (1/2*Lambda[1] - Lambda[2], -1/2*Lambda[1] + Lambda[2]) (1/2*Lambda[1] - Lambda[2], -1/2*Lambda[1] + Lambda[2])
                (Lambda[1] - 2*Lambda[2],) (-Lambda[1] + 2*Lambda[2],)
                (-Lambda[1] - Lambda[2],) (Lambda[1] + Lambda[2],)
                (2*Lambda[1] - Lambda[2],) (-2*Lambda[1] + Lambda[2],)
                (-Lambda[1] + 1/2*Lambda[2], Lambda[1] - 1/2*Lambda[2]) (-Lambda[1] + 1/2*Lambda[2], Lambda[1] - 1/2*Lambda[2])
                (-2*Lambda[1] + Lambda[2],) (2*Lambda[1] - Lambda[2],)
            """
            if len(self.value) == 0:
                return self
            dual_path = [-v for v in self.value]
            dual_path.reverse()
            return self.parent()(tuple(dual_path))

        def f(self, i, power=1, to_string_end=False, length_only=False):
            r"""
            Returns the `i`-th crystal lowering operator on ``self``.

            INPUT:

            - ``i`` -- element of the index set of the underlying root system
            - ``power`` -- positive integer; specifies the power of the lowering operator
              to be applied (default: 1)
            - ``to_string_end`` -- boolean; if set to True, returns the anti-dominant end of the
              `i`-string of ``self``. (default: False)
            - ``length_only`` -- boolean; if set to True, returns the distance to the anti-dominant
              end of the `i`-string of ``self``.

            EXAMPLES::

                sage: C = CrystalOfLSPaths(['A',2],[1,1])
                sage: c = C.module_generators[0]
                sage: c.f(1)
                (-Lambda[1] + 2*Lambda[2],)
                sage: c.f(1,power=2)
                sage: c.f(2)
                (2*Lambda[1] - Lambda[2],)
                sage: c.f(2,to_string_end=True)
                (2*Lambda[1] - Lambda[2],)
                sage: c.f(2,length_only=True)
                1

                sage: C = CrystalOfLSPaths(['A',2,1],[-1,-1,2])
                sage: c = C.module_generators[0]
                sage: c.f(2,power=2)
                (Lambda[0] + Lambda[1] - 2*Lambda[2],)
            """
            dual_path = self.dualize()
            dual_path = dual_path.e(i, power, to_string_end, length_only)
            if length_only:
                return dual_path
            if dual_path == None:
                return None
            return dual_path.dualize()

        def s(self, i):
            r"""
            Computes the reflection of ``self`` along the `i`-string.

            This method is more efficient than the generic implementation since it uses
            powers of `e` and `f` in the Littelmann model directly.

            EXAMPLES::

                sage: C = CrystalOfLSPaths(['A',2],[1,1])
                sage: c = C.module_generators[0]
                sage: c.s(1)
                (-Lambda[1] + 2*Lambda[2],)
                sage: c.s(2)
                (2*Lambda[1] - Lambda[2],)

                sage: C = CrystalOfLSPaths(['A',2,1],[-1,0,1])
                sage: c = C.module_generators[0]; c
                (-Lambda[0] + Lambda[2],)
                sage: c.s(2)
                (Lambda[1] - Lambda[2],)
                sage: c.s(1)
                (-Lambda[0] + Lambda[2],)
                sage: c.f(2).s(1)
                (Lambda[0] - Lambda[1],)
            """
            ph = self.phi(i)
            ep = self.epsilon(i)
            diff = ph - ep
            if diff >= 0:
                return self.f(i, power=diff)
            else:
                return self.e(i, power=-diff)

        def _latex_(self):
            r"""
            Latex method for ``self``.

            EXAMPLES::

                sage: C = CrystalOfLSPaths(['A',2],[1,1])
                sage: c = C.module_generators[0]
                sage: c._latex_()
                [\Lambda_{1} + \Lambda_{2}]
            """
            return [latex(p) for p in self.value]


class CrystalOfProjectedLevelZeroLSPaths(CrystalOfLSPaths):
    r"""
    Crystal of projected level zero LS paths.

    INPUT:

    - ``weight`` -- a dominant weight of the weight space of an affine Kac-Moody root system

    When ``weight`` is just a single fundamental weight `\Lambda_r`, this crystal is
    isomorphic to a Kirillov-Reshetikhin (KR) crystal, see also
    :meth:`sage.combinat.crystals.kirillov_reshetikhin.KirillovReshetikhinCrystalFromLSPaths`.
    For general weights, it is isomorphic to a tensor product of single-column KR crystals.

    EXAMPLES::

        sage: R = RootSystem(['C',3,1])
        sage: La = R.weight_space().basis()
        sage: LS = CrystalOfProjectedLevelZeroLSPaths(La[1]+La[3])
        sage: LS.cardinality()
        84
        sage: GLS = LS.digraph()

        sage: K1 = KirillovReshetikhinCrystal(['C',3,1],1,1)
        sage: K3 = KirillovReshetikhinCrystal(['C',3,1],3,1)
        sage: T = TensorProductOfCrystals(K3,K1)
        sage: T.cardinality()
        84
        sage: GT = T.digraph() # long time
        sage: GLS.is_isomorphic(GT, edge_labels = True) # long time
        True
    """

    @staticmethod
    def __classcall_private__(cls, weight):
        """
        Classcall to mend the input.

        Internally, the CrystalOfProjectedLevelZeroLSPaths uses a level zero weight,
        which is passed on to CrystalOfLSPaths. ``weight`` is first coerced to
        a level zero weight.

        TESTS::

            sage: R = RootSystem(['C',3,1])
            sage: La = R.weight_space().basis()
            sage: C = CrystalOfProjectedLevelZeroLSPaths(La[1] + La[2])
            sage: C2 = CrystalOfProjectedLevelZeroLSPaths(La[1] + La[2])
            sage: C is C2
            True
        """
        La = weight.parent().basis()
        weight = weight - (weight.level())*La[0]
        return super(CrystalOfLSPaths, cls).__classcall__(cls, weight)

    def one_dimensional_configuration_sum(self, q = None, group_components = True):
        r"""
        Computes the one-dimensional configuration sum for untwisted types.

        INPUT:

        - ``q`` -- (default: ``None``) a variable or ``None``; if ``None``,
          a variable `q` is set in the code
        - ``group_components`` -- (default: ``True``) boolean; if ``True``,
          then the terms are grouped by classical component

        The one-dimensional configuration sum is the sum of the weights of all elements in the crystal
        weighted by the energy function.

        .. WARNING::

            The one-dimensional configuration sum using LS paths is currently only implemented for
            untwisted types!

        EXAMPLES::

            sage: R = RootSystem(['A',2,1])
            sage: La = R.weight_space().basis()
            sage: LS = CrystalOfProjectedLevelZeroLSPaths(2*La[1])
            sage: LS.one_dimensional_configuration_sum()
            B[-2*Lambda[1] + 2*Lambda[2]] + (q+1)*B[-Lambda[1]]
            + (q+1)*B[Lambda[1] - Lambda[2]] + B[2*Lambda[1]] + B[-2*Lambda[2]] + (q+1)*B[Lambda[2]]
            sage: R.<t> = ZZ[]
            sage: LS.one_dimensional_configuration_sum(t, False)
            B[-2*Lambda[1] + 2*Lambda[2]] + (t+1)*B[-Lambda[1]] + (t+1)*B[Lambda[1] - Lambda[2]]
            + B[2*Lambda[1]] + B[-2*Lambda[2]] + (t+1)*B[Lambda[2]]

        TESTS::

            sage: R = RootSystem(['B',3,1])
            sage: La = R.weight_space().basis()
            sage: LS = CrystalOfProjectedLevelZeroLSPaths(La[1]+La[2])
            sage: LS.one_dimensional_configuration_sum() == LS.one_dimensional_configuration_sum(group_components=False) # long time
            True
            sage: K1 = KirillovReshetikhinCrystal(['B',3,1],1,1)
            sage: K2 = KirillovReshetikhinCrystal(['B',3,1],2,1)
            sage: T = TensorProductOfCrystals(K2,K1)
            sage: T.one_dimensional_configuration_sum() == LS.one_dimensional_configuration_sum()
            True
        """
        if q is None:
            from sage.rings.all import QQ
            q = QQ['q'].gens()[0]
        P0 = self.weight_lattice_realization().classical()
        B = P0.algebra(q.parent())
        if group_components:
            G = self.digraph(index_set = self.cartan_type().classical().index_set())
            C = G.connected_components()
            return sum(q**(c[0].energy_function())*B.sum(B(P0(b.weight())) for b in c) for c in C)
        return B.sum(q**(b.energy_function())*B(P0(b.weight())) for b in self)


    class Element(CrystalOfLSPaths.Element):
        """
        Element of a crystal of projected level zero LS paths.
        """

        @cached_in_parent_method
        def scalar_factors(self):
            r"""
            Obtain the scalar factors for ``self``.

            Each LS path (or ``self``) can be written as a piecewise linear map

            .. MATH::

                \pi(t) = \sum_{u'=1}^{u-1} (\sigma_{u'} - \sigma_{u'-1}) \nu_{u'} + (t-\sigma_{u-1}) \nu_{u}

            for `0<\sigma_1<\sigma_2<\cdots<\sigma_s=1` and `\sigma_{u-1} \le t \le \sigma_{u}` and `1 \le u \le s`.
            This method returns the tuple of `(\sigma_1,\ldots,\sigma_s)`.

            EXAMPLES::

                sage: R = RootSystem(['C',3,1])
                sage: La = R.weight_space().basis()
                sage: LS = CrystalOfProjectedLevelZeroLSPaths(La[1]+La[3])
                sage: b = LS.module_generators[0]
                sage: b.scalar_factors()
                [1]
                sage: c = b.f(1).f(3).f(2)
                sage: c.scalar_factors()
                [1/3, 1]
            """
            weight = self.parent().weight
            l = []
            s = 0
            for c in self.value:
                supp = c.support()
                if len(supp) > 0:
                    for w in weight.orbit():
                        i = supp[0]
                        # Check whether the vectors c and w are positive scalar multiples of each other
                        if i in w.support() and c[i]*w[i] > 0 and c[i]*w == w[i]*c:
                            s += c[i] / w[i]
                            l += [s]
                            break
            return l

        @cached_in_parent_method
        def weyl_group_representation(self):
            r"""
            Transforms the weights in the LS path ``self`` to elements in the Weyl group.

            Each LS path can be written as the piecewise linear map:

            .. MATH::

                \pi(t) = \sum_{u'=1}^{u-1} (\sigma_{u'} - \sigma_{u'-1}) \nu_{u'} + (t-\sigma_{u-1}) \nu_{u}

            for `0<\sigma_1<\sigma_2<\cdots<\sigma_s=1` and `\sigma_{u-1} \le t \le \sigma_{u}` and `1 \le u \le s`.
            Each weight `\nu_u` is also associated to a Weyl group element. This method returns the list
            of Weyl group elements associated to the `\nu_u` for `1\le u\le s`.

            EXAMPLES::

                sage: R = RootSystem(['C',3,1])
                sage: La = R.weight_space().basis()
                sage: LS = CrystalOfProjectedLevelZeroLSPaths(La[1]+La[3])
                sage: b = LS.module_generators[0]
                sage: c = b.f(1).f(3).f(2)
                sage: c.weyl_group_representation()
                [s2*s3*s1, s3*s1]
            """
            weight = self.parent().weight
            level = -weight.coefficient(0)
            La = weight.parent().fundamental_weights()
            cartan = weight.parent().cartan_type().classical()
            W = WeylGroup(cartan,prefix='s')
            scalars = [0] + self.scalar_factors()
            l = [(self.value[i]/(scalars[i+1]-scalars[i])+level*La[0]).to_dominant_chamber(reduced_word=True) for i in range(len(scalars)-1)]
            return [W.from_reduced_word(a[1]) for a in l]

        @cached_in_parent_method
        def energy_function(self):
            r"""
            Returns the energy function of ``self`` for untwisted types.

            For level zero LS paths `\pi \in \mathbb{B}_\mathrm{cl}(\lambda)`, the energy function is defined as follows:

            .. MATH::

                D(\pi)=-\sum_{u=1}^{s-1} (1-\sigma_{u}) \langle \lambda,\mathrm{wt}(b_{u}) \rangle

            To make sense of this equation, we first need some definitions.
            Let us write the LS path (or ``self``) as a piecewise linear map

            .. MATH::

                \pi(t)=\sum_{u'=1}^{u-1} (\sigma_{u'}-\sigma_{u'-1})x_{u'}+(t-\sigma_{u-1})x_{u}

            for `\sigma_{u-1} \le t \le \sigma_{u}` and `1 \le u \le s`.
            Here `b_{u}` is a shortest directed path from `x_{u+1}` to `x_{u}` in the parabolic quantum
            Bruhat graph.

            For any `x,y\in W/W_J`, where `W_J` is a parabolic subgroup of `W` (the stabilizer of the weight `\lambda`), let

            .. MATH::

                d: x= w_{0} \stackrel{\beta_{1}}{\leftarrow}
                w_{1} \stackrel{\beta_{2}}{\leftarrow} \cdots
                \stackrel{\beta_{n}}{\leftarrow} w_{n}=y

            be a shortest path in the parabolic quantum Bruhat graph. The weight is defined as

            .. MATH::

                \mathrm{wt}(d):=\sum_{ \begin{subarray}{c}
                1 \le k \le n \text{ such that } \\
                w_{k-1} \stackrel{\beta_{k}}{\leftarrow} w_{k}
                \text{ is a down arrow}
                \end{subarray}
                }
                \beta_{k}^{\vee}.

            For more information, see [LNSSS2013]_.

            REFERENCES:

            .. [LNSSS2013] C. Lenart, S. Naito, D. Sagaki, A. Schilling, M. Shimozono,
               A uniform model for Kirillov-Reshetikhin crystals. Extended abstract.
               DMTCS proc, to appear ( {{{:arXiv:`1211.6019`}}} )

            .. WARNING::

                The energy function for LS paths is currently only implemented for
                untwisted types!


            EXAMPLES::

                sage: R = RootSystem(['C',3,1])
                sage: La = R.weight_space().basis()
                sage: LS = CrystalOfProjectedLevelZeroLSPaths(La[1]+La[3])
                sage: b = LS.module_generators[0]
                sage: c = b.f(1).f(3).f(2)
                sage: c.energy_function()
                0
                sage: c=b.e(0)
                sage: c.energy_function()
                1

                sage: R = RootSystem(['A',2,1])
                sage: La = R.weight_space().basis()
                sage: LS = CrystalOfProjectedLevelZeroLSPaths(2*La[1])
                sage: b = LS.module_generators[0]
                sage: c = b.e(0)
                sage: c.energy_function()
                1
                sage: [c.energy_function() for c in sorted(LS.list())]
                [0, 1, 0, 0, 0, 1, 0, 1, 0]

            The next test checks that the energy function is constant on classically connected components::

                sage: R = RootSystem(['A',2,1])
                sage: La = R.weight_space().basis()
                sage: LS = CrystalOfProjectedLevelZeroLSPaths(2*La[1]+La[2])
                sage: G = LS.digraph(index_set=[1,2])
                sage: C = G.connected_components()
                sage: [all(c[0].energy_function()==a.energy_function() for a in c) for c in C]
                [True, True, True, True]
            """
            weight = self.parent().weight
            c_weight = weight.parent().classical()(weight)
            cartan = weight.parent().cartan_type().classical()
            W = WeylGroup(cartan,prefix='s')
            R = RootSystem(cartan).coroot_lattice()
            G = W.quantum_bruhat_graph(tuple(weight.weyl_stabilizer()))
            L = self.weyl_group_representation()
            paths = [G.shortest_path(L[i+1],L[i]) for i in range(len(L)-1)]
            paths_labels = [[G.edge_label(p[i],p[i+1]) for i in range(len(p)-1) if p[i].length()+1 != p[i+1].length()] for p in paths]
            scalars = self.scalar_factors()
            return sum((1-scalars[i])*c_weight.scalar( R.sum(root.associated_coroot()
                       for root in paths_labels[i]) ) for i in range(len(paths_labels)))

