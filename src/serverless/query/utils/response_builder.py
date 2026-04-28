def finish_success(inspector, answer: str, vectors: list[dict]):
    sources = list({
        (v.get("metadata") or {}).get("source_key", "")
        for v in vectors
        if v.get("metadata")
    })

    inspector.addAttribute("sources_used", sources)
    inspector.addAttribute("answer", answer)
    inspector.addAttribute("status", "Answer generated successfully")
    return inspector.finish()


def finish_error(inspector, message: str):
    inspector.addAttribute("error", message)
    inspector.addAttribute("status", "failed")
    return inspector.finish()


def finish_no_results(inspector):
    inspector.addAttribute("status", "No relevant documents found")
    return inspector.finish()


def finish_debug(inspector):
    inspector.addAttribute("status", "debug_ok")
    return inspector.finish()