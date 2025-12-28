from pathlib import Path
import re
import yaml

skills_dir = Path('skills')
for skill_md in skills_dir.rglob('*/SKILL.md'):
    try:
        rel_path = skill_md.parent.relative_to(skills_dir)
        skill_name = str(rel_path).replace('\\', '/')
        print(f'Loading: {skill_name}')
        print(f'  Path: {skill_md}')
        
        content = skill_md.read_text()
        match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if match:
            frontmatter = yaml.safe_load(match.group(1))
            print(f'  Frontmatter: {frontmatter.get("name") if frontmatter else "None"}')
    except Exception as e:
        print(f'  Error: {e}')
