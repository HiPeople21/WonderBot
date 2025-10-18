# Vectors: Foundations, Spaces, and the Gram-Schmidt Process

**Estimated reading time:** 35 minutes  
**Learning order:** Vectors and Operations → Vector Spaces → Bases and Dimension → Orthogonality and Projections → Gram-Schmidt Process

---

## Vectors and Operations

Vectors are ordered lists of numbers representing quantities with both magnitude and direction. They can be added, subtracted, and multiplied by scalars. Vector operations are foundational in mathematics and physics, enabling the description of geometric and physical phenomena. Understanding vector arithmetic is essential for working with higher-level concepts like vector spaces and orthogonality.

### Key Points
- A vector in **ℝⁿ** is an *n*-tuple of real numbers.  
- Vector addition and scalar multiplication are defined component-wise.  
- The zero vector has all components zero.  
- The length (norm) of a vector is its distance from the origin.  
- Vectors can be represented graphically as arrows.

### Formulas
\[
u + v = (u_1 + v_1, \ldots, u_n + v_n)
\]  
\[
c\,u = (c\,u_1, \ldots, c\,u_n)
\]  
\[
\|u\| = \sqrt{u_1^2 + \cdots + u_n^2}
\]  
\[
u \cdot v = u_1 v_1 + \cdots + u_n v_n
\]

### Worked Example
**Compute** \( u + v \) **and** \( 2u \) **for** \( u = (1, 3), v = (4, -2) \).  
- Add components: (1 + 4, 3 + (-2)) = (5, 1)  
- Multiply u by 2: (2×1, 2×3) = (2, 6)  

**Answer:** \( u + v = (5, 1),\ 2u = (2, 6) \)

### Diagram
*Vector addition in ℝ²:*  
Draw two arrows from the origin: one for **u**, one for **v**. Draw **u + v** as the diagonal of the parallelogram formed by **u** and **v**.

### Common Pitfalls
- Confusing vector and scalar multiplication.  
- Forgetting to add or multiply each component.  
- Mixing up vector and matrix notation.

### Quick Quiz
- What is the zero vector in ℝ³?  
  **Ans:** (0, 0, 0)  
- How do you compute the length of (3, 4)?  
  **Ans:** √(3² + 4²) = 5  
- Is (2, -1) a vector in ℝ²?  
  **Ans:** Yes  

---

## Vector Spaces

A vector space is a set of vectors closed under addition and scalar multiplication, satisfying specific axioms. Vector spaces generalize the concept of vectors beyond ℝⁿ, allowing for abstract mathematical structures. Subspaces are subsets that themselves form vector spaces. Understanding vector spaces is crucial for linear algebra and applications in science and engineering.

### Key Points
- A vector space has closure under addition and scalar multiplication.  
- It contains the zero vector and additive inverses.  
- Subspaces are vector spaces within a larger vector space.  
- Common examples: ℝⁿ, space of polynomials, matrices.

### Formulas
\[
u, v \in V \implies u + v \in V
\]  
\[
c \in \mathbb{R},\ u \in V \implies c\,u \in V
\]

### Worked Example
**Is the set** \( W = \{(x, y, 0) \mid x, y \in \mathbb{R}\} \) **a subspace of** ℝ³?

- Check zero vector: (0, 0, 0) is in W.  
- Closure under addition: (x_1, y_1, 0) + (x_2, y_2, 0) = (x_1 + x_2, y_1 + y_2, 0) ∈ W.  
- Closure under scalar multiplication: \( c(x, y, 0) = (cx, cy, 0) \in W \).  

**Answer:** Yes, W is a subspace of ℝ³.

### Diagram
*Subspace in ℝ³:*  
Draw ℝ³ as a cube or box. Shade a plane through the origin to represent a subspace.

### Common Pitfalls
- Forgetting to check all subspace conditions.  
- Assuming any subset is a subspace.  
- Ignoring the requirement for the zero vector.

### Quick Quiz
- Does every vector space have a zero vector?  
  **Ans:** Yes  
- Is the set of all (x, 1) in ℝ² a subspace?  
  **Ans:** No, it does not contain the zero vector.  
- What is a subspace?  
  **Ans:** A subset that is itself a vector space.  

---

## Bases and Dimension

A basis of a vector space is a set of linearly independent vectors that span the space. The number of vectors in a basis is the dimension of the space. Bases provide a coordinate system for expressing any vector uniquely as a linear combination. Understanding bases and dimension is essential for solving systems and understanding structure in linear algebra.

### Key Points
- A basis is a minimal spanning set of linearly independent vectors.  
- Every vector in the space can be written uniquely as a linear combination of basis vectors.  
- The dimension is the number of vectors in any basis.  
- Changing the basis changes coordinates but not the underlying vector.

### Formulas
\[
\text{If } B = \{v_1, \ldots, v_n\} \text{ is a basis, then } \dim(V) = n
\]  
\[
\text{Any } v \in V:\ v = a_1 v_1 + \cdots + a_n v_n
\]

### Worked Example
**Find a basis and the dimension of** \( W = \{(x, 2x) \mid x \in \mathbb{R}\} \) **in** ℝ².  
- Express a general vector: (x, 2x) = x(1, 2).  
- The set \(\{(1, 2)\}\) spans W and is linearly independent.  

**Answer:** Basis = \(\{(1, 2)\}\); Dimension = 1.

### Diagram
*Basis vectors in ℝ²:*  
Draw two non-parallel arrows from the origin, labeled \(e_1\) and \(e_2\), spanning the plane.

### Common Pitfalls
- Confusing spanning sets with bases.  
- Forgetting to check linear independence.  
- Assuming the standard basis is the only basis.

### Quick Quiz
- What is the dimension of ℝ³?  
  **Ans:** 3  
- Can a basis have more vectors than the dimension?  
  **Ans:** No  
- What property must basis vectors have?  
  **Ans:** Linear independence  

---

## Orthogonality and Projections

Two vectors are orthogonal if their dot product is zero. Orthogonality is central to geometry and simplifies computations in vector spaces. Projections allow us to decompose vectors into components parallel and perpendicular to a given direction. These concepts are foundational for constructing orthonormal bases and for the Gram-Schmidt process.

### Key Points
- Orthogonal vectors have zero dot product.  
- An orthonormal set is both orthogonal and each vector has unit length.  
- The projection of \(u\) onto \(v\) is the component of \(u\) in the direction of \(v\).  
- Orthogonality simplifies calculations and interpretations.

### Formulas
\[
u \cdot v = 0 \implies u, v \text{ are orthogonal}
\]  
\[
\operatorname{proj}_v(u) = \frac{u \cdot v}{v \cdot v}\, v
\]

### Worked Example
**Find the projection of** \( u = (3, 4) \) **onto** \( v = (1, 0) \).  
- Compute dot product: \(u\cdot v = 3\times 1 + 4\times 0 = 3\).  
- Compute \(v\cdot v = 1\times 1 + 0\times 0 = 1\).  
- \(\operatorname{proj}_v(u) = (3/1)(1, 0) = (3, 0)\).  

**Answer:** The projection is (3, 0).

### Diagram
*Projection of \(u\) onto \(v\):*  
Draw vectors \(u\) and \(v\) from the origin. Draw a dashed line from the tip of \(u\) perpendicular to \(v\), meeting \(v\) at the projection point.

### Common Pitfalls
- Forgetting to divide by \(v\cdot v\) in the projection formula.  
- Assuming orthogonal means perpendicular in all contexts.  
- Not normalizing vectors when required for orthonormality.

### Quick Quiz
- What is the dot product of (1, 2) and (2, -1)?  
  **Ans:** \(1\times 2 + 2\times (-1) = 0\)  
- When are two vectors orthogonal?  
  **Ans:** When their dot product is zero.  
- What is an orthonormal set?  
  **Ans:** A set of orthogonal unit vectors.  

---

## Gram-Schmidt Process

The Gram-Schmidt process converts a set of linearly independent vectors into an orthonormal set spanning the same subspace. It works by iteratively subtracting projections to ensure orthogonality, then normalizing. This process is essential in constructing orthonormal bases, simplifying computations, and is widely used in numerical algorithms.

### Key Points
- Transforms any basis into an orthonormal basis.  
- Works by subtracting projections to enforce orthogonality.  
- Each new vector is normalized to have unit length.  
- Preserves the span of the original set.

### Formulas
\[
\begin{aligned}
u_1 &= v_1, \\
u_2 &= v_2 - \operatorname{proj}_{u_1}(v_2), \\
u_k &= v_k - \sum_{j=1}^{k-1} \operatorname{proj}_{u_j}(v_k), \\
e_k &= \frac{u_k}{\|u_k\|}.
\end{aligned}
\]

### Worked Example
**Apply Gram-Schmidt to** \( v_1 = (1, 1),\ v_2 = (1, 0) \) **in** ℝ².  
1. \( u_1 = v_1 = (1, 1) \)  
2. \( \operatorname{proj}_{u_1}(v_2) = \dfrac{(1,0)\cdot(1,1)}{1^2+1^2}(1,1) = \dfrac{1}{2}(1,1) = (0.5, 0.5) \)  
3. \( u_2 = v_2 - \operatorname{proj}_{u_1}(v_2) = (1,0) - (0.5,0.5) = (0.5,-0.5) \)  
4. Normalize:  
   - \( e_1 = \dfrac{(1,1)}{\sqrt{2}} \)  
   - \( e_2 = \dfrac{(0.5,-0.5)}{\sqrt{0.5}} = \left(\dfrac{1}{\sqrt{2}}, -\dfrac{1}{\sqrt{2}}\right) \)

**Answer:**  
Orthonormal basis:  
\[
\left\{ \left(\tfrac{1}{\sqrt{2}}, \tfrac{1}{\sqrt{2}}\right),\ \left(\tfrac{1}{\sqrt{2}}, -\tfrac{1}{\sqrt{2}}\right) \right\}
\]

### Diagram
*Gram-Schmidt in ℝ²:*  
Draw \(v_1\) and \(v_2\) as non-parallel arrows. Draw \(u_1 = v_1\). Then draw \(u_2\) as \(v_2\) minus its projection onto \(u_1\), showing the orthogonal direction.

### Common Pitfalls
- Forgetting to subtract *all* previous projections.  
- Not normalizing the orthogonal vectors.  
- Applying to linearly dependent vectors (process fails).

### Quick Quiz
- What does Gram-Schmidt produce?  
  **Ans:** An orthonormal basis.  
- What must the input vectors be?  
  **Ans:** Linearly independent.  
- What is the first step in Gram-Schmidt?  
  **Ans:** Set \( u_1 = v_1 \).  

---

## Summary

This packet introduces vectors, their operations, and the structure of vector spaces. It explains the concepts of bases and dimension, orthogonality, and projections, culminating in the **Gram-Schmidt process** for constructing orthonormal bases.  
Mastery of these topics is essential for advanced study in **linear algebra** and its applications.
