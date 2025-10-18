# Vectors and Vector Spaces: Foundations and Gram-Schmidt Process

**Estimated reading time:** 35 minutes

**Learning order:**
Vectors: Definitions and Operations → Vector Spaces: Structure and Properties → Bases and Dimension → Gram-Schmidt Process: Orthogonalization

## Vectors: Definitions and Operations

A vector is an ordered list of numbers representing magnitude and direction in space. Vectors can be added, scaled, and used to describe geometric and physical phenomena. Understanding vectors is essential for studying vector spaces and linear algebra. Key operations include addition, scalar multiplication, and the dot product. Vectors are represented as columns or rows, and their properties are foundational for higher concepts.

**Key points:**
- **A vector is an element of** \(\mathbb{R}^n\) *(n-dimensional real space)*.
- **Vector addition and scalar multiplication** are basic operations.
- **The dot product** measures similarity and length.
- **Vectors can be represented geometrically as arrows.**
- **Zero vector** has all components zero.

**Formulas:**
- Addition: \(\vec{a} + \vec{b} = (a_1 + b_1, ..., a_n + b_n)\)
- Scalar multiplication: \(c\vec{a} = (c a_1, ..., c a_n)\)
- Dot product: \(\vec{a} \cdot \vec{b} = \sum_{i=1}^n a_i b_i\)
- Norm: \(||\vec{a}|| = \sqrt{\vec{a} \cdot \vec{a}}\)

**Worked Example:**
*Add vectors* \(\vec{a} = (2, 1)\) *and* \(\vec{b} = (1, 3)\).
- Add corresponding components: \(2 + 1 = 3\), \(1 + 3 = 4\).
- Resulting vector: \((3, 4)\).
**Answer:** (3, 4)

**Diagram:**
Two vectors in \(\mathbb{R}^2\) and their sum.
*Instructions: Draw two arrows from the origin: one to (2,1), another to (1,3). Draw a third arrow from the origin to (3,4), showing vector addition.*

**Common Pitfalls:**
- Confusing vector addition with multiplication.
- Forgetting to add components individually.
- Misinterpreting the direction of vectors.
- Ignoring the zero vector's role.

**Quick Quiz:**
- What is the dot product of (1,2) and (3,4)?
  **Ans:** \(1 \times 3 + 2 \times 4 = 11\)
- What is the norm of (3,4)?
  **Ans:** 5
- Is (0,0) a vector?
  **Ans:** Yes, it is the zero vector.

---

## Vector Spaces: Structure and Properties

A vector space is a set of vectors closed under addition and scalar multiplication. It must satisfy specific axioms, such as associativity, distributivity, and the existence of a zero vector. Vector spaces provide a framework for linear algebra, allowing the study of linear combinations, subspaces, and transformations. Understanding vector spaces is crucial for grasping bases, dimension, and orthogonalization.

**Key points:**
- **A vector space is a set with two operations:** addition and scalar multiplication.
- **Closure under operations** is required.
- **Zero vector and additive inverses exist.**
- **Subspaces are subsets that are also vector spaces.**
- **Axioms include associativity, distributivity, and identity.**

**Formulas:**
- Closure: \(\forall \vec{u}, \vec{v} \in V, \vec{u} + \vec{v} \in V\)
- Scalar multiplication: \(\forall c \in \mathbb{R}, \vec{v} \in V, c\vec{v} \in V\)

**Worked Example:**
*Show that the set of all vectors (x, 0) in \(\mathbb{R}^2\) forms a subspace.*
- Check closure under addition: \((x_1, 0) + (x_2, 0) = (x_1 + x_2, 0)\).
- Check closure under scalar multiplication: \(c(x, 0) = (cx, 0)\).
- Zero vector: \((0, 0)\) is included.
**Answer:** Yes, it is a subspace.

**Diagram:**
A vector space and a subspace within it.
*Instructions: Draw a large oval labeled V. Inside, draw a smaller oval labeled W, showing W as a subspace of V.*

**Common Pitfalls:**
- Assuming any subset is a subspace.
- Ignoring closure requirements.
- Forgetting the zero vector.
- Confusing vector spaces with sets of points.

**Quick Quiz:**
- Does (1,2) belong to the subspace of (x,0)?
  **Ans:** No
- Is the set \(\{(0,0)\}\) a vector space?
  **Ans:** Yes, called the trivial space.
- What operation must a vector space be closed under?
  **Ans:** Addition and scalar multiplication.

---

## Bases and Dimension

A basis of a vector space is a set of linearly independent vectors that span the space. The number of vectors in a basis defines the dimension of the space. Bases allow unique representation of every vector as a linear combination of basis vectors. Understanding bases is essential for coordinate systems, transformations, and orthogonalization methods like Gram-Schmidt.

**Key points:**
- **Basis:** minimal set of linearly independent vectors spanning the space.
- **Dimension:** number of vectors in any basis.
- **Every vector is a unique linear combination of basis vectors.**
- **Changing basis changes coordinates but not the space.**
- **Orthonormal bases simplify calculations.**

**Formulas:**
- Linear independence: \(\sum_{i=1}^n c_i \vec{v}_i = 0 \implies c_i = 0 \forall i\)
- Span: \(\text{span}\{\vec{v}_1, ..., \vec{v}_n\} = \{\sum_{i=1}^n c_i \vec{v}_i\}\)

**Worked Example:**
*Is \(\{(1,0), (0,1)\}\) a basis for \(\mathbb{R}^2\)?*
- Check linear independence: No scalar multiples.
- Check spanning: Any \((x, y) = x(1,0) + y(0,1)\).
**Answer:** Yes, it is a basis.

**Diagram:**
Basis vectors in \(\mathbb{R}^2\).
*Instructions: Draw two arrows from the origin: one to (1,0), another to (0,1). Show that any vector in \(\mathbb{R}^2\) can be reached by combining these.*

**Common Pitfalls:**
- Using dependent vectors as a basis.
- Confusing spanning with independence.
- Assuming more vectors means higher dimension.
- Forgetting uniqueness of representation.

**Quick Quiz:**
- How many vectors in a basis for \(\mathbb{R}^3\)?
  **Ans:** Three
- Can \(\{(1,1), (2,2)\}\) be a basis for \(\mathbb{R}^2\)?
  **Ans:** No, they are dependent.
- What does dimension mean?
  **Ans:** Number of vectors in a basis.

---

## Gram-Schmidt Process: Orthogonalization

The Gram-Schmidt process converts a set of linearly independent vectors into an orthogonal (or orthonormal) basis. This is useful for simplifying calculations and constructing coordinate systems. The process subtracts projections to ensure each new vector is orthogonal to the previous ones. The result is a set of vectors that are mutually perpendicular, and if normalized, have unit length.

**Key points:**
- **Gram-Schmidt creates orthogonal (or orthonormal) bases.**
- **Works only for linearly independent vectors.**
- **Each step subtracts the projection onto previous vectors.**
- **Orthonormal bases have vectors of length one.**
- **Useful for QR decomposition and simplifying problems.**

**Formulas:**
- First vector: \(\vec{u}_1 = \vec{v}_1\)
- Second: \(\vec{u}_2 = \vec{v}_2 - \text{proj}_{\vec{u}_1}(\vec{v}_2)\)
- Projection: \(\text{proj}_{\vec{u}}(\vec{v}) = \frac{\vec{v} \cdot \vec{u}}{||\vec{u}||^2} \vec{u}\)
- Normalize: \(\vec{e}_i = \frac{\vec{u}_i}{||\vec{u}_i||}\)

**Worked Example:**
*Apply Gram-Schmidt to (1,1) and (1,0) in \(\mathbb{R}^2\).*
- Set \(\vec{u}_1 = (1,1)\).
- Compute projection: \(\text{proj}_{u_1}(v_2) = \frac{(1,0) \cdot (1,1)}{1^2 + 1^2} (1,1) = \frac{1}{2}(1,1) = (0.5, 0.5)\).
- Subtract: \(\vec{u}_2 = (1,0) - (0.5,0.5) = (0.5,-0.5)\).
**Answer:** Orthogonal basis: (1,1), (0.5,-0.5)

**Diagram:**
Gram-Schmidt orthogonalization in \(\mathbb{R}^2\).
*Instructions: Draw two non-parallel arrows from the origin. Show the projection of the second onto the first, and the orthogonalized result as a new arrow perpendicular to the first.*

**Common Pitfalls:**
- Applying to dependent vectors.
- Forgetting to subtract all previous projections.
- Not normalizing for orthonormal basis.
- Arithmetic errors in projection calculation.

**Quick Quiz:**
- What does Gram-Schmidt produce?
  **Ans:** An orthogonal (or orthonormal) basis.
- What is the projection formula?
  **Ans:** \(\text{proj}_{u}(v) = \frac{v \cdot u}{||u||^2} u\)
- Why normalize vectors?
  **Ans:** To get unit length (orthonormal basis).

---

## Summary

This packet introduces vectors, their operations, and the structure of vector spaces. It explains bases and dimension, then details the Gram-Schmidt process for orthogonalization. Each section builds on the previous, providing definitions, formulas, examples, diagrams, and quizzes. Mastery of these concepts is essential for advanced linear algebra and applications in science and engineering.
