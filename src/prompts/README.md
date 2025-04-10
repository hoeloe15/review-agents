# Prompts Directory

This directory contains the prompt templates used by the document review plugins.

## Structure

- `/critic/` - Prompts for the critical analysis perspective
  - `system_prompt.txt` - System prompt establishing the critic persona
  - `user_prompt.txt` - Template for the user prompt (uses {title} and {document} placeholders)

- `/innovator/` - Prompts for the innovative, visionary perspective
  - `system_prompt.txt` - System prompt establishing the innovator persona
  - `user_prompt.txt` - Template for the user prompt (uses {title} and {document} placeholders)

- `/synthesizer/` - Prompts for synthesizing multiple perspectives
  - `system_prompt.txt` - System prompt establishing the synthesizer persona
  - `user_prompt.txt` - Template for the user prompt (uses {title}, {innovative_feedback}, and {critical_feedback} placeholders)

## Usage

The plugins automatically load these prompts at initialization time. To modify the behavior of the agents without changing code, simply edit these text files.

## Best Practices

1. Keep prompts focused on their specific role
2. Use consistent formatting in templates
3. Test prompt changes thoroughly before deployment
4. Document any significant changes to prompts
