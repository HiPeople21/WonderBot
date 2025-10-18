# Vectors: Foundations, Vector Spaces, and the Gram-Schmidt Process

**Estimated reading time:** 28 minutes

**Learning order:** Introduction to Vectors → Vector Spaces and Subspaces → Linear Independence and Basis → The Gram-Schmidt Process

## Introduction to Vectors

Vectors are mathematical objects characterized by both magnitude and direction. They are fundamental in physics, engineering, and mathematics. Vectors can be represented as ordered lists of numbers (components) in a coordinate system. Operations on vectors include addition, scalar multiplication, and the dot product. Understanding vectors is essential for studying higher-dimensional spaces and linear algebra concepts.

**Key points:**
- A **vector** is an ordered list of numbers, often written as \((v_1, v_2, ..., v_n)\).
- **Vector addition** and **scalar multiplication** are the basic operations.
- The **length (norm)** of a vector is a measure of its magnitude.
- The **dot product** measures the similarity (angle) between two vectors.

**Formulas:**

\[
v + w = (v_1 + w_1,\, v_2 + w_2,\, \ldots,\, v_n + w_n)
\]

\[
c\, v = (c\, v_1,\, c\, v_2,\, \ldots,\, c\, v_n)
\]

\[
\|v\| = \sqrt{v_1^2 + v_2^2 + \ldots + v_n^2}
\]

\[
v \cdot w = v_1 w_1 + v_2 w_2 + \ldots + v_n w_n
\]

**Worked Example:**

*Add vectors \(v = (2, 1)\) and \(w = (1, 3)\). Find their sum and the norm of the result.*

- Add corresponding components: \((2+1,\, 1+3) = (3, 4)\).
- Compute the norm: \(\sqrt{3^2 + 4^2} = \sqrt{9 + 16} = \sqrt{25} = 5\).

**Answer:** The sum is \((3, 4)\) and its norm is \(5\).

**Diagram:** Vector addition in 2D
*Instructions: Draw two arrows from the origin: one to (2,1), another to (1,3). Draw the sum vector from the origin to (3,4). Show the parallelogram formed.*

**Common Pitfalls:**
- Confusing vector addition with multiplication.
- Forgetting to add components individually.
- Misinterpreting the norm as a vector instead of a scalar.

**Quick Quiz:**
- What is the sum of (1,2) and (3,4)?
  **Ans:** (4,6)
- What is the norm of (0,5)?
  **Ans:** 5
- What is the dot product of (1,2) and (3,4)?
  **Ans:** 11

---

## Vector Spaces and Subspaces

A **vector space** is a set of vectors closed under addition and scalar multiplication, following specific rules (axioms). **Subspaces** are subsets of vector spaces that are themselves vector spaces. Understanding these structures is crucial for analyzing systems of equations, transformations, and more advanced linear algebra topics.

**Key points:**
- A vector space must satisfy closure, associativity, distributivity, and contain a zero vector.
- Subspaces must contain the zero vector and be closed under addition and scalar multiplication.
- Common examples: \(\mathbb{R}^n\), the set of all n-dimensional real vectors.
- The **span** of a set of vectors is the smallest subspace containing them.

**Formulas:**

\[
\mathrm{Span}(S) = \left\{ c_1 v_1 + \ldots + c_k v_k \mid c_i \in \mathbb{R} \right\}
\]

\[
\text{Zero vector: } 0 = (0, 0, \ldots, 0)
\]

**Worked Example:**

*Is the set of all vectors \((x, y, 0)\) in \(\mathbb{R}^3\) a subspace?*

- Check if the zero vector \((0,0,0)\) is included: Yes, set \(x=0, y=0\).
- Check closure under addition: \((x_1, y_1, 0) + (x_2, y_2, 0) = (x_1+x_2, y_1+y_2, 0)\). Still in the set.
- Check closure under scalar multiplication: \(c(x, y, 0) = (cx, cy, 0)\). Still in the set.

**Answer:** Yes, it is a subspace of \(\mathbb{R}^3\).

**Diagram:** A subspace in \(\mathbb{R}^3\)
*Instructions: Draw a 3D coordinate system. Shade a plane through the origin to represent a subspace. Mark the origin.*

**Common Pitfalls:**
- Forgetting to check for the zero vector.
- Assuming any subset is a subspace.
- Ignoring closure under both operations.

**Quick Quiz:**
- Does the set \(\{(x, 0) \mid x \in \mathbb{R}\}\) form a subspace of \(\mathbb{R}^2\)?
  **Ans:** Yes
- Is the set \(\{(x, 1) \mid x \in \mathbb{R}\}\) a subspace of \(\mathbb{R}^2\)?
  **Ans:** No
- What is the span of \(\{(1,0), (0,1)\}\) in \(\mathbb{R}^2\)?
  **Ans:** All of \(\mathbb{R}^2\)

---

## Linear Independence and Basis

A set of vectors is **linearly independent** if no vector in the set can be written as a linear combination of the others. A **basis** is a set of linearly independent vectors that spans the entire vector space. The number of vectors in a basis is called the **dimension** of the space. These concepts are essential for understanding the structure of vector spaces and for applications such as solving systems of equations.

**Key points:**
- Linear independence means no vector is redundant.
- A basis is both linearly independent and spans the space.
- The dimension is the number of vectors in any basis.
- Every vector in the space can be uniquely written as a linear combination of basis vectors.

**Formulas:**

\[
c_1 v_1 + c_2 v_2 + \ldots + c_k v_k = 0 \implies c_1 = c_2 = \ldots = c_k = 0
\]

\[
\dim(V) = \text{number of vectors in a basis}
\]

**Worked Example:**

*Are the vectors \((1,2)\) and \((2,4)\) linearly independent in \(\mathbb{R}^2\)?*

- Set up equation: \(c_1 (1,2) + c_2 (2,4) = (0,0)\).
- This gives two equations: \(c_1 + 2c_2 = 0\) and \(2c_1 + 4c_2 = 0\).
- Second equation is just twice the first, so infinite solutions.
- Nontrivial solution exists (e.g., \(c_1 = 2, c_2 = -1\)).

**Answer:** No, they are linearly dependent.

**Diagram:** Basis vectors in \(\mathbb{R}^2\)
*Instructions: Draw the x and y axes. Draw arrows from the origin to (1,0) and (0,1). Label them as basis vectors.*

**Common Pitfalls:**
- Assuming any set of vectors is independent.
- Confusing spanning with independence.
- Forgetting that basis vectors must be both independent and spanning.

**Quick Quiz:**
- What is the dimension of \(\mathbb{R}^3\)?
  **Ans:** 3
- Can a basis for \(\mathbb{R}^2\) have three vectors?
  **Ans:** No
- Are (1,0,0), (0,1,0), (0,0,1) a basis for \(\mathbb{R}^3\)?
  **Ans:** Yes

---

## The Gram-Schmidt Process

The **Gram-Schmidt process** converts a set of linearly independent vectors into an orthogonal (or orthonormal) set spanning the same subspace. This is useful for simplifying computations and for applications in projections and least squares. The process works by iteratively subtracting projections onto previously constructed orthogonal vectors.

**Key points:**
- Transforms any independent set into an orthogonal set.
- Orthogonal vectors have zero dot product.
- Orthonormal sets are orthogonal and each vector has norm 1.
- Useful for constructing bases for subspaces.

**Formulas:**

\[
u_1 = v_1
\]

\[
u_2 = v_2 - \frac{v_2 \cdot u_1}{u_1 \cdot u_1} u_1
\]

\[
u_k = v_k - \sum_{j=1}^{k-1} \frac{v_k \cdot u_j}{u_j \cdot u_j} u_j
\]

\[
e_k = \frac{u_k}{\|u_k\|} \quad \text{(orthonormal version)}
\]

**Worked Example:**

*Apply Gram-Schmidt to \(v_1 = (1,1)\), \(v_2 = (1,0)\) in \(\mathbb{R}^2\).*

- Set \(u_1 = v_1 = (1,1)\).
- Compute projection:
  \[
  \text{proj} = \frac{(1,0)\cdot(1,1)}{(1,1)\cdot(1,1)} (1,1) = \frac{1}{2} (1,1) = (0.5, 0.5)
  \]
- \(u_2 = v_2 - \text{proj} = (1,0) - (0.5,0.5) = (0.5, -0.5)\)

**Answer:** Orthogonal set: \((1,1), (0.5,-0.5)\).

**Diagram:** Orthogonalization in 2D
*Instructions: Draw two non-parallel vectors from the origin. Show the projection of the second onto the first, then draw the orthogonalized second vector.*

**Common Pitfalls:**
- Forgetting to subtract all previous projections.
- Not normalizing for orthonormal sets.
- Applying to dependent vectors (process fails).

**Quick Quiz:**
- What is the first step in Gram-Schmidt?
  **Ans:** Set \(u_1 = v_1\).
- What does it mean for vectors to be orthogonal?
  **Ans:** Their dot product is zero.
- Can Gram-Schmidt be applied to dependent vectors?
  **Ans:** No

---

## Summary

This packet introduces vectors, vector spaces, linear independence, bases, and the Gram-Schmidt process. It builds from basic vector operations to the structure of vector spaces and the construction of orthogonal bases. Mastery of these concepts is essential for advanced study in linear algebra and its applications.


# Practice Problems

---

## Problem 0

**Gram-Schmidt:**
Let \( \mathbf{v}_1 = (1, 1, 0) \), \( \mathbf{v}_2 = (1, 0, 1) \), \( \mathbf{v}_3 = (0, 1, 1) \).
Use the Gram-Schmidt process to find an orthonormal basis for the subspace of \( \mathbb{R}^3 \) spanned by \( \mathbf{v}_1, \mathbf{v}_2, \mathbf{v}_3 \).

---

## Problem 1

**Vector Spaces:**
Let \( V \) be the set of all \( 2 \times 2 \) real matrices.
Show that \( V \) is a vector space over \( \mathbb{R} \).

---

## Problem 2

**Gram-Schmidt:**
Apply the Gram-Schmidt process to the vectors \( \mathbf{v}_1 = (1, 0, 1) \), \( \mathbf{v}_2 = (1, 1, 0) \) in \( \mathbb{R}^3 \) to obtain an orthonormal basis.

---

## Problem 3

**Vector Spaces:**
Let \( W \) be the set of all vectors in \( \mathbb{R}^3 \) of the form \( (a, a, a) \) where \( a \in \mathbb{R} \).
Is \( W \) a subspace of \( \mathbb{R}^3 \)? Find a basis for \( W \).

---

## Problem 4

**Vector Spaces:**
Let \( U \) be the set of all vectors in \( \mathbb{R}^3 \) of the form \( (a, b, 0) \) where \( a, b \in \mathbb{R} \).
Is \( U \) a subspace of \( \mathbb{R}^3 \)? Find a basis for \( U \).

---

# Solutions

---

## 1. Gram-Schmidt for \( \mathbf{v}_1, \mathbf{v}_2, \mathbf{v}_3 \)

**Step 1:**
Set \( \mathbf{u}_1 = \mathbf{v}_1 = (1, 1, 0) \)

\[
e_1 = \frac{\mathbf{u}_1}{\|\mathbf{u}_1\|} = \frac{(1, 1, 0)}{\sqrt{1^2 + 1^2 + 0^2}} = \frac{(1, 1, 0)}{\sqrt{2}}
\]

**Step 2:**
\[
\mathbf{u}_2 = \mathbf{v}_2 - \operatorname{proj}_{\mathbf{u}_1}(\mathbf{v}_2)
\]
\[
\operatorname{proj}_{\mathbf{u}_1}(\mathbf{v}_2) = \frac{\mathbf{v}_2 \cdot \mathbf{u}_1}{\mathbf{u}_1 \cdot \mathbf{u}_1} \mathbf{u}_1
\]
\[
\mathbf{v}_2 \cdot \mathbf{u}_1 = 1 \qquad \mathbf{u}_1 \cdot \mathbf{u}_1 = 2
\]
\[
\operatorname{proj}_{\mathbf{u}_1}(\mathbf{v}_2) = \frac{1}{2}(1, 1, 0) = (0.5, 0.5, 0)
\]
\[
\mathbf{u}_2 = (1, 0, 1) - (0.5, 0.5, 0) = (0.5, -0.5, 1)
\]
\[
\|\mathbf{u}_2\| = \sqrt{0.5^2 + (-0.5)^2 + 1^2} = \sqrt{1.5}
\]
\[
e_2 = \frac{\mathbf{u}_2}{\|\mathbf{u}_2\|} = \frac{(0.5, -0.5, 1)}{\sqrt{1.5}}
\]

**Step 3:**
\[
\mathbf{u}_3 = \mathbf{v}_3 - \operatorname{proj}_{\mathbf{u}_1}(\mathbf{v}_3) - \operatorname{proj}_{\mathbf{u}_2}(\mathbf{v}_3)
\]
\[
\mathbf{v}_3 \cdot \mathbf{u}_1 = 1
\]
\[
\operatorname{proj}_{\mathbf{u}_1}(\mathbf{v}_3) = \frac{1}{2}(1, 1, 0) = (0.5, 0.5, 0)
\]
\[
\mathbf{v}_3 \cdot \mathbf{u}_2 = 0.5
\]
\[
\mathbf{u}_2 \cdot \mathbf{u}_2 = 1.5
\]
\[
\operatorname{proj}_{\mathbf{u}_2}(\mathbf{v}_3) = \frac{0.5}{1.5}(0.5, -0.5, 1) = \left(\frac{1}{3}, -\frac{1}{3}, \frac{1}{3}\right)
\]
\[
\mathbf{u}_3 = (0, 1, 1) - (0.5, 0.5, 0) - \left(\frac{1}{3}, -\frac{1}{3}, \frac{1}{3}\right) = \left(-\frac{5}{6}, \frac{5}{6}, \frac{2}{3}\right)
\]
\[
\|\mathbf{u}_3\| = \sqrt{\left(-\frac{5}{6}\right)^2 + \left(\frac{5}{6}\right)^2 + \left(\frac{2}{3}\right)^2} = \sqrt{\frac{66}{36}} = \sqrt{\frac{11}{6}}
\]
\[
e_3 = \frac{\mathbf{u}_3}{\|\mathbf{u}_3\|}
\]

**Orthonormal basis:**
\[
e_1 = \frac{(1, 1, 0)}{\sqrt{2}}
\]
\[
e_2 = \frac{(0.5, -0.5, 1)}{\sqrt{1.5}}
\]
\[
e_3 = \frac{(-5/6, 5/6, 2/3)}{\sqrt{11/6}}
\]

---

## 2. Vector Space of \( 2 \times 2 \) Matrices

To show that \( V \) is a vector space over \( \mathbb{R} \):

- **Closure under addition:** If \( A \) and \( B \) are \( 2 \times 2 \) matrices, then \( A + B \) is also \( 2 \times 2 \).
- **Closure under scalar multiplication:** If \( A \) is \( 2 \times 2 \) and \( c \in \mathbb{R} \), then \( cA \) is \( 2 \times 2 \).
- **Existence of zero vector:** The zero matrix is in \( V \).
- **Existence of additive inverses:** For any \( A \) in \( V \), \( -A \) is in \( V \).
- **Associativity, commutativity, distributivity** follow from matrix properties.

Therefore, \( V \) is a vector space over \( \mathbb{R} \).

---

## 3. Gram-Schmidt for \( \mathbf{v}_1, \mathbf{v}_2 \)

**Step 1:**
Set \( \mathbf{u}_1 = \mathbf{v}_1 = (1, 0, 1) \)

\[
e_1 = \frac{\mathbf{u}_1}{\|\mathbf{u}_1\|} = \frac{(1, 0, 1)}{\sqrt{1^2 + 0^2 + 1^2}} = \frac{(1, 0, 1)}{\sqrt{2}}
\]

**Step 2:**
\[
\mathbf{u}_2 = \mathbf{v}_2 - \operatorname{proj}_{\mathbf{u}_1}(\mathbf{v}_2)
\]
\[
\operatorname{proj}_{\mathbf{u}_1}(\mathbf{v}_2) = \frac{\mathbf{v}_2 \cdot \mathbf{u}_1}{\mathbf{u}_1 \cdot \mathbf{u}_1} \mathbf{u}_1
\]
\[
\mathbf{v}_2 \cdot \mathbf{u}_1 = 1 \qquad \mathbf{u}_1 \cdot \mathbf{u}_1 = 2
\]
\[
\operatorname{proj}_{\mathbf{u}_1}(\mathbf{v}_2) = \frac{1}{2}(1, 0, 1) = (0.5, 0, 0.5)
\]
\[
\mathbf{u}_2 = (1, 1, 0) - (0.5, 0, 0.5) = (0.5, 1, -0.5)
\]
\[
\|\mathbf{u}_2\| = \sqrt{0.5^2 + 1^2 + (-0.5)^2} = \sqrt{1.5}
\]
\[
e_2 = \frac{\mathbf{u}_2}{\|\mathbf{u}_2\|} = \frac{(0.5, 1, -0.5)}{\sqrt{1.5}}
\]

**Orthonormal basis:**
\[
e_1 = \frac{(1, 0, 1)}{\sqrt{2}}
\]
\[
e_2 = \frac{(0.5, 1, -0.5)}{\sqrt{1.5}}
\]

---

## 4. Subspace \( W \subset \mathbb{R}^3 \) of the form \( (a, a, a) \)

- The zero vector \( (0, 0, 0) \) is in \( W \).
- If \( \mathbf{u} = (a, a, a) \), \( \mathbf{v} = (b, b, b) \), then \( \mathbf{u} + \mathbf{v} = (a+b, a+b, a+b) \in W \).
- If \( c \in \mathbb{R} \), \( c\mathbf{u} = (ca, ca, ca) \in W \).

Therefore, \( W \) is a subspace of \( \mathbb{R}^3 \).

**Basis for \( W \):**
\[
\{ (1, 1, 1) \}
\]

---

## 5. Subspace \( U \subset \mathbb{R}^3 \) of the form \( (a, b, 0) \)

- The zero vector \( (0, 0, 0) \) is in \( U \).
- If \( \mathbf{u} = (a, b, 0) \), \( \mathbf{v} = (c, d, 0) \), then \( \mathbf{u} + \mathbf{v} = (a+c, b+d, 0) \in U \).
- If \( k \in \mathbb{R} \), \( k\mathbf{u} = (ka, kb, 0) \in U \).

Therefore, \( U \) is a subspace of \( \mathbb{R}^3 \).

**Basis for \( U \):**
\[
\{ (1, 0, 0),\ (0, 1, 0) \}
\]