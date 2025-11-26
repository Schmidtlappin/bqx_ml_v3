# BQX ML V3 BUILDER AGENT - START HERE

**Welcome Builder Agent!**

This sandbox contains all the documentation and resources you need to complete the BQX ML V3 implementation.

## 📚 REQUIRED READING (IN ORDER)

1. **[BQX_ML_V3_BUILDER_CHARGE.md](./BQX_ML_V3_BUILDER_CHARGE.md)**
   - Your formal responsibility assignment
   - Core mandate: BUILD, DON'T SIMULATE
   - Quality gates and acceptance criteria

2. **[BQX_ML_V3_BUILDER_BRIEFING.md](./BQX_ML_V3_BUILDER_BRIEFING.md)**
   - Current infrastructure status
   - What exists vs what needs to be built
   - Immediate next steps to execute

3. **[BUILDER_AGENT_WORKSPACE_GUIDE.md](./BUILDER_AGENT_WORKSPACE_GUIDE.md)**
   - Workspace navigation
   - Intelligence file protocols
   - Compliance expectations
   - Sandbox usage guidelines

## 🧠 INTELLIGENCE FILES TO INGEST

Before starting any work, load these files:
- `/home/micha/bqx_ml_v3/intelligence/context.json`
- `/home/micha/bqx_ml_v3/intelligence/semantics.json`
- `/home/micha/bqx_ml_v3/intelligence/ontology.json`

## 🚀 QUICK START

```bash
# 1. Load intelligence files
python3 << EOF
import json
with open('/home/micha/bqx_ml_v3/intelligence/context.json') as f:
    context = json.load(f)
print(f"Project: {context['project']['name']}")
print(f"Tasks: {context['project_management']['stages']} stages")
EOF

# 2. Check AirTable status
python3 /home/micha/bqx_ml_v3/scripts/check_airtable_status.py

# 3. Begin with first task
# MP03.P01.S01.T01 - "Prepare training dataset"
```

## ⚠️ CRITICAL REMINDERS

1. **EVERY implementation must be REAL** - No simulations
2. **Use ROWS BETWEEN, never RANGE BETWEEN** - Interval-centric only
3. **Update AirTable after each task** - With real verification
4. **Maintain intelligence files** - Update as you create infrastructure
5. **Work in this sandbox** - Test here before production

## 📊 CURRENT STATUS

- **Total Tasks**: 197
- **Completed**: 0 (all reset to Todo)
- **Your Goal**: Complete ALL 197 with real infrastructure

## 🆘 SUPPORT

If you encounter blockers:
1. Document in AirTable task notes
2. Keep task as "In Progress"
3. Chief Engineer will review through AirTable

---

**BEGIN BY READING ALL THREE DOCUMENTS IN ORDER**

Good luck, Builder Agent! The success of BQX ML V3 depends on your real implementation.