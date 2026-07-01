# similarity.mojo
# Module Mojo -- calcul de similarite cosine optimise (exigence du sujet :
# couple Python/Mojo). Absent du projet original.
# Mojo exploite la vectorisation SIMD et la parallelisation automatique
# pour accelerer le calcul sur de gros corpus.

from math import sqrt
from algorithm import parallelize, vectorize
from memory import memset_zero
from sys.info import simdwidthof

alias float32 = DType.float32
alias SIMD_WIDTH = simdwidthof[float32]()


fn cosine_similarity(
    a: DTypePointer[float32],
    b: DTypePointer[float32],
    n: Int,
) -> Float32:
    """Similarite cosine entre deux vecteurs de dimension n (vectorise SIMD)."""
    var dot: Float32 = 0.0
    var norm_a: Float32 = 0.0
    var norm_b: Float32 = 0.0

    @parameter
    fn _inner[width: Int](i: Int):
        let va = a.simd_load[width](i)
        let vb = b.simd_load[width](i)
        dot += (va * vb).reduce_add()
        norm_a += (va * va).reduce_add()
        norm_b += (vb * vb).reduce_add()

    vectorize[_inner, SIMD_WIDTH](n)

    let denom = sqrt(norm_a) * sqrt(norm_b)
    if denom == 0.0:
        return 0.0
    return dot / denom


fn top_k_cosine(
    query: DTypePointer[float32],
    corpus: DTypePointer[float32],
    n_docs: Int,
    dim: Int,
    k: Int,
    out_indices: DTypePointer[DType.int32],
    out_scores: DTypePointer[float32],
):
    """Retourne les k documents les plus similaires a la requete (parallelise)."""
    var scores = DTypePointer[float32].alloc(n_docs)
    memset_zero(scores, n_docs)

    @parameter
    fn compute_score(doc_idx: Int):
        let doc_ptr = corpus.offset(doc_idx * dim)
        scores[doc_idx] = cosine_similarity(query, doc_ptr, dim)

    parallelize[compute_score](n_docs)

    for i in range(k):
        var best_idx = i
        for j in range(i + 1, n_docs):
            if scores[j] > scores[best_idx]:
                best_idx = j
        let tmp_score = scores[i]
        scores[i] = scores[best_idx]
        scores[best_idx] = tmp_score
        out_indices[i] = best_idx
        out_scores[i] = scores[i]

    scores.free()
