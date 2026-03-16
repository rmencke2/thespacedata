def build_logo_prompt(project: dict) -> str:
    return f"""
You are a senior brand designer. Create a clean, scalable logo.

Brand: {project['brand_name']}
Tagline: {project.get('tagline') or '—'}
Industry: {project.get('industry', '')}
Personality/values: {project.get('values', '')}
Style keywords: {project.get('style_keywords', '')}
Color constraints: {project.get('colors', '')}
Icon direction: {project.get('icon_ideas', '')}

Deliver 3 distinct compositions: wordmark, wordmark+left icon, stacked icon above.
Flat vector look, no 3D, no photo, no tiny details. Include a mono variant.
Transparent or light solid background with margin.
"""