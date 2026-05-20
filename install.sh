#!/usr/bin/env sh
set -eu

RAW="https://raw.githubusercontent.com/giltotherescue/velocity-agent-skills/main"
CACHE_BUST="${CACHE_BUST:-$(date +%s)}"
DESTINATIONS="$HOME/.agents/skills $HOME/.claude/skills"
SKILLS="vl-cook vl-stage vl-screenshot vl-handoff"

for base in $DESTINATIONS; do
  mkdir -p "$base"

  for skill in $SKILLS; do
    mkdir -p "$base/$skill"
    curl -fsSL "$RAW/skills/$skill/SKILL.md?$CACHE_BUST" -o "$base/$skill/SKILL.md"

    if [ "$skill" = "vl-screenshot" ]; then
      mkdir -p "$base/$skill/scripts"
      curl -fsSL "$RAW/skills/$skill/scripts/build_contact_sheet.py?$CACHE_BUST" -o "$base/$skill/scripts/build_contact_sheet.py"
      chmod +x "$base/$skill/scripts/build_contact_sheet.py"
    fi
  done
done

echo "Installed Velocity Skills:"
echo "  ~/.agents/skills/vl-cook"
echo "  ~/.agents/skills/vl-stage"
echo "  ~/.agents/skills/vl-screenshot"
echo "  ~/.agents/skills/vl-handoff"
echo "  ~/.claude/skills/vl-cook"
echo "  ~/.claude/skills/vl-stage"
echo "  ~/.claude/skills/vl-screenshot"
echo "  ~/.claude/skills/vl-handoff"
