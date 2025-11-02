#!/usr/bin/env fish

# Add frontmatter to agent-os commands for Claude Code

set commands_dir .claude/commands/agent-os

# Command metadata
set -l descriptions \
    "create-tasks:Break spec into implementation tasks:implementation" \
    "implement-tasks:Implement tasks with verification:implementation" \
    "improve-skills:Improve project-specific skills:utility" \
    "orchestrate-tasks:Advanced multi-agent task orchestration:implementation" \
    "shape-spec:Initialize and shape feature specification:specification" \
    "write-spec:Write detailed feature specification:specification"

for entry in $descriptions
    set parts (string split ':' $entry)
    set cmd_name $parts[1]
    set desc $parts[2]
    set category $parts[3]

    set file $commands_dir/$cmd_name.md

    if test -f $file
        # Check if frontmatter already exists
        if not head -1 $file | grep -q "^---\$"
            # Create temp file with frontmatter
            echo "---" > $file.tmp
            echo "name: $cmd_name" >> $file.tmp
            echo "description: \"$desc\"" >> $file.tmp
            echo "category: $category" >> $file.tmp
            echo "---" >> $file.tmp
            echo "" >> $file.tmp
            cat $file >> $file.tmp
            mv $file.tmp $file
            echo "✓ Added frontmatter to $cmd_name.md"
        else
            echo "• $cmd_name.md already has frontmatter"
        end
    end
end

echo ""
echo "Frontmatter added! Commands should now appear in Claude Code."
