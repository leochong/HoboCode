from hobo_code.skills.registry import SkillRegistry

r = SkillRegistry()
r.load_skills()
skills = r.list_skills()
forward = [s for s in skills if '/' in s]
backslash = [s for s in skills if '\\' in s]
print('Forward slash skills:', forward[:3])
print('Backslash skills:', backslash[:3])

python_skill = r.get_skill('language/python_expert')
print('python_expert:', python_skill)

# Check what's in anthropic_skills
print('Python-related keys:', [k for k in r._anthropic_skills.keys() if 'python' in k.lower()])
