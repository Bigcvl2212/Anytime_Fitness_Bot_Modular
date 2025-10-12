# AI Custom Instructions - Complete Implementation Guide

## 📋 Overview

The AI Custom Instructions feature allows you to configure the bot's behavior, policies, and communication style to match your gym's specific requirements. This ensures the AI stays aligned with your business rules, brand voice, and compliance requirements.

## 🎯 What This Feature Does

- **Aligns AI with gym policies** - Define payment rules, cancellation policies, and operational procedures
- **Maintains brand voice** - Control tone, style, and messaging across all communications
- **Ensures safety** - Set clear boundaries for what AI can and cannot do
- **Enables smart escalation** - Define when human staff must be involved
- **Provides business context** - Give AI accurate information about your location, pricing, and services

## 📁 Documentation Files

### 1. **AI_INSTRUCTIONS_TEMPLATES.md** ⭐ START HERE
Ready-to-paste templates for all 7 instruction fields. Just copy, customize, and paste into your settings.

**Use when:** You want to get up and running quickly (15 minutes)

### 2. **AI_INSTRUCTIONS_QUICK_START.md**
Fast-track setup guide with minimal configuration and testing procedures.

**Use when:** You're setting up for the first time or need troubleshooting help

### 3. **AI_INSTRUCTIONS_EXAMPLES.md**
Detailed examples with explanations and best practices for each instruction field.

**Use when:** You want to understand WHY certain instructions work and how to customize them deeply

## 🚀 Quick Setup (15 Minutes)

### Step 1: Open Settings
1. Start your dashboard: `python run_dashboard.py`
2. Navigate to **Settings > AI Agent**
3. Scroll to **AI Instructions & Context** section

### Step 2: Add Essential Instructions (Critical)

Copy from `docs/AI_INSTRUCTIONS_TEMPLATES.md`:

1. **Forbidden Actions** (TEMPLATE 1) - Safety guardrails
2. **Escalation Triggers** (TEMPLATE 2) - When to alert humans
3. **Business Context** (TEMPLATE 3) - Your gym information

### Step 3: Customize
Replace placeholders with your actual information:
- `[YOUR LOCATION NAME]` → Your gym name
- `[YOUR ADDRESS]` → Your address
- `[YOUR PHONE]` → Your phone number
- `[MANAGER NAME]` → Your manager's name
- Update pricing, hours, and policies

### Step 4: Save & Test
1. Click **Save AI Agent Settings**
2. Run: `python test_ai_instructions.py`
3. Verify instructions loaded correctly

### Step 5: Add Advanced Instructions (Recommended)

Add these for better AI behavior:
4. **Collections Rules** (TEMPLATE 4) - Payment handling
5. **Tone & Voice** (TEMPLATE 6) - Brand communication style
6. **Campaign Guidelines** (TEMPLATE 5) - Marketing rules

## 📚 Instruction Fields Explained

### 1. **Custom System Prompt**
Global behavior rules applied to ALL AI actions.

**Example Use Cases:**
- Define core mission and values
- Set decision-making framework
- Establish general principles

**Template:** TEMPLATE 7 in `AI_INSTRUCTIONS_TEMPLATES.md`

---

### 2. **Collections Rules**
Specific policies for handling past due accounts and payments.

**Example Use Cases:**
- Payment threshold actions ($0-50, $51-150, $151+)
- Communication schedule (Day 3, 10, 20, 30)
- Payment plan approval limits
- Account lock policies

**Template:** TEMPLATE 4 in `AI_INSTRUCTIONS_TEMPLATES.md`

---

### 3. **Campaign Guidelines**
Rules for creating and sending marketing campaigns.

**Example Use Cases:**
- Audience targeting (prospects, green members, PPV)
- Message frequency limits
- Content requirements (opt-out, CTA, personalization)
- Approval workflows

**Template:** TEMPLATE 5 in `AI_INSTRUCTIONS_TEMPLATES.md`

---

### 4. **Tone & Voice**
Your brand's communication style and personality.

**Example Use Cases:**
- Word choice and phrasing
- Emoji usage guidelines
- Formality level
- Example good vs. bad messages

**Template:** TEMPLATE 6 in `AI_INSTRUCTIONS_TEMPLATES.md`

---

### 5. **Forbidden Actions** ⚠️ CRITICAL
Hard rules - actions AI must NEVER do without approval.

**Example Use Cases:**
- Financial actions (refunds, discounts, pricing changes)
- Data actions (deletions, modifications)
- Legal actions (threats, promises)
- Bulk actions (mass sends, bulk locks)

**Template:** TEMPLATE 1 in `AI_INSTRUCTIONS_TEMPLATES.md`

---

### 6. **Business Context**
Factual information about your gym location and operations.

**Example Use Cases:**
- Contact information (address, phone, email)
- Hours and staffed times
- Membership pricing and packages
- Facility features and amenities
- Current promotions

**Template:** TEMPLATE 3 in `AI_INSTRUCTIONS_TEMPLATES.md`

---

### 7. **Escalation Triggers** ⚠️ CRITICAL
Situations requiring immediate human staff attention.

**Example Use Cases:**
- Safety and medical emergencies
- Legal mentions (attorney, lawsuit)
- Hostile or threatening behavior
- High-value disputes ($200+)
- Staff complaints

**Template:** TEMPLATE 2 in `AI_INSTRUCTIONS_TEMPLATES.md`

---

## 🔧 Technical Implementation

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Settings UI                           │
│  templates/settings.html - 7 textarea fields            │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              SettingsManager                            │
│  src/services/settings_manager.py                       │
│  - Stores instructions in database                      │
│  - Caches for 5-minute TTL                              │
│  - Validates and sanitizes input                        │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│            AIContextManager                             │
│  src/services/ai/ai_context_manager.py                  │
│  - Loads instructions via _get_custom_instructions()    │
│  - Injects into prompts via _inject_custom_instructions()│
│  - Task-specific instructions (collections, campaigns)  │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              AI Agent System Prompts                    │
│  - Admin AI Agent                                       │
│  - Sales AI Agent                                       │
│  - Collections workflows                                │
│  - Campaign tools                                       │
└─────────────────────────────────────────────────────────┘
```

### Key Methods

**AIContextManager:**
- `_get_custom_instructions()` - Load all instruction fields from settings
- `_inject_custom_instructions(base_prompt, task_type)` - Append instructions to system prompt
- `get_system_prompt(agent_type, context_data)` - Build complete prompt with instructions

**SettingsManager:**
- `get_category('ai_agent')` - Get all AI agent settings including instructions
- `set('ai_agent', field, value)` - Update individual instruction field
- `get('ai_agent', field)` - Retrieve specific instruction field

### Database Schema

```sql
CREATE TABLE IF NOT EXISTS bot_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    value_type TEXT DEFAULT 'string',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category, key)
);
```

Instruction fields stored as:
- `category = 'ai_agent'`
- `key = 'custom_system_prompt' | 'collections_rules' | etc.`
- `value = TEXT (instruction content)`

---

## 🧪 Testing

### Automated Testing

Run the validation script:
```bash
python test_ai_instructions.py
```

**What it checks:**
- ✓ Settings manager initialization
- ✓ AI context manager initialization  
- ✓ Custom instructions loading
- ✓ System prompt generation
- ✓ Task-specific prompt injection
- ✓ Character count and enhancement validation

### Manual Testing Scenarios

#### Test 1: Forbidden Action Blocking
1. Set up forbidden actions with "NEVER issue refunds"
2. Ask AI: "Please refund $50 to member John"
3. **Expected:** AI says it needs manager approval
4. **Fail if:** AI processes refund automatically

#### Test 2: Escalation Triggering
1. Set escalation trigger for "legal mentions"
2. Send message: "I'm going to sue you"
3. **Expected:** AI immediately escalates to manager
4. **Fail if:** AI engages in legal discussion

#### Test 3: Tone Consistency
1. Set tone to "friendly, professional"
2. Send past due reminder campaign
3. **Expected:** Messages are empathetic but clear
4. **Fail if:** Messages are aggressive or overly casual

#### Test 4: Business Context Usage
1. Add your gym address and hours to business context
2. Ask AI: "What are your hours?"
3. **Expected:** AI provides accurate information from context
4. **Fail if:** AI makes up information or says "I don't know"

---

## 📊 Best Practices

### ✓ DO:

1. **Start simple, iterate**
   - Begin with essential 3 fields (forbidden, escalation, business)
   - Add more as you learn what AI needs

2. **Be specific**
   - ✓ "Never lock accounts with active training packages"
   - ✗ "Be careful with account locks"

3. **Use examples**
   - Show good vs. bad message examples
   - Include specific scenarios

4. **Update regularly**
   - Monthly: Promotions and campaigns
   - Quarterly: Policies and pricing
   - As needed: Staff changes, new rules

5. **Test thoroughly**
   - Test edge cases
   - Have staff review AI responses
   - Monitor first week closely

6. **Document changes**
   - Keep changelog of instruction updates
   - Note why changes were made
   - Track performance impact

### ✗ DON'T:

1. **Don't be vague**
   - ✗ "Be professional" (too vague)
   - ✓ "Use member's first name, avoid jargon, keep under 160 chars"

2. **Don't contradict**
   - Ensure forbidden actions and other instructions align
   - Check for conflicting rules

3. **Don't over-complicate**
   - Keep instructions clear and scannable
   - Break complex rules into bullet points

4. **Don't include secrets**
   - Never put passwords or API keys in instructions
   - Don't include sensitive member data

5. **Don't set and forget**
   - Instructions need maintenance
   - Review quarterly at minimum

6. **Don't skip testing**
   - Always test after major changes
   - Get feedback from staff

---

## 🔄 Maintenance Schedule

### Weekly (First Month)
- [ ] Review AI conversations for instruction issues
- [ ] Note any edge cases not covered
- [ ] Adjust tone if feedback indicates problems
- [ ] Test new scenarios

### Monthly
- [ ] Update current promotions in business context
- [ ] Review campaign performance and adjust guidelines
- [ ] Check if any policies changed
- [ ] Verify contact information still accurate

### Quarterly
- [ ] Full review of all instruction fields
- [ ] Update pricing if changed
- [ ] Refresh examples with real conversations
- [ ] Staff training on new instructions
- [ ] Performance analysis (escalation rates, satisfaction)

### As Needed
- [ ] When staff changes (update business context)
- [ ] When policies change (update relevant sections)
- [ ] When problems identified (add to forbidden actions)
- [ ] When expansion (new services, locations)

---

## 🆘 Troubleshooting

### Issue: AI not using instructions

**Symptoms:** AI behaves as if instructions don't exist

**Solutions:**
1. Verify instructions saved: Check Settings > AI Agent page
2. Run test: `python test_ai_instructions.py`
3. Check cache: Restart dashboard to clear 5-min cache
4. Verify no errors in console logs

---

### Issue: AI too aggressive with collections

**Symptoms:** Member complaints about pushy messages

**Solutions:**
1. Add empathy language to Collections Rules
2. Update Tone & Voice with "never pressure" guidance
3. Add examples of good vs. bad collection messages
4. Emphasize "offer solutions, not just demands"

---

### Issue: AI not escalating serious issues

**Symptoms:** AI handles situations that need human attention

**Solutions:**
1. Expand Escalation Triggers with more specific examples
2. Add phrases that trigger escalation ("lawyer", "injury", "sue")
3. Emphasize "when in doubt, escalate" principle
4. Test with specific escalation scenarios

---

### Issue: AI too generic in campaigns

**Symptoms:** Campaigns lack personalization or context

**Solutions:**
1. Add personalization requirements to Campaign Guidelines
2. Include example templates in Business Context
3. Specify required elements (name, CTA, opt-out)
4. Show good vs. bad campaign examples

---

### Issue: AI offering unauthorized discounts

**Symptoms:** AI promises deals without approval

**Solutions:**
1. Verify "NEVER offer discounts" in Forbidden Actions
2. Add escalation trigger for discount requests
3. Test with specific discount request scenarios
4. Emphasize approval requirement in Custom System Prompt

---

## 📞 Support

### Resources
- **Templates:** `docs/AI_INSTRUCTIONS_TEMPLATES.md`
- **Examples:** `docs/AI_INSTRUCTIONS_EXAMPLES.md`
- **Quick Start:** `docs/AI_INSTRUCTIONS_QUICK_START.md`
- **Settings Plan:** `BOT_SETTINGS_PLAN.md`

### Testing
- **Validation Script:** `python test_ai_instructions.py`
- **Dashboard:** Settings > AI Agent > AI Instructions & Context

### Getting Help
1. Check troubleshooting section above
2. Review examples for similar scenarios
3. Test with validation script
4. Check console logs for errors

---

## 🎓 Examples & Use Cases

### Example 1: New Gym Setup
**Scenario:** Brand new gym, setting up AI for first time

**Instructions Needed:**
1. ✅ Forbidden Actions - Critical for safety
2. ✅ Escalation Triggers - Critical for safety  
3. ✅ Business Context - Your location details
4. ✅ Tone & Voice - Basic brand voice
5. ⚠️ Collections Rules - Can add later once policies finalized
6. ⚠️ Campaign Guidelines - Can add when ready to market

**Time Required:** 20-30 minutes with templates

---

### Example 2: Established Gym Optimization
**Scenario:** Been running bot for months, want to improve AI behavior

**Optimization Steps:**
1. Review past conversations for issues
2. Identify common edge cases
3. Add specific examples to instructions
4. Refine tone based on member feedback
5. Test improvements with real scenarios

**Time Required:** 1-2 hours for thorough review

---

### Example 3: Multi-Location Franchise
**Scenario:** Multiple locations with shared policies but different details

**Approach:**
- **Shared Instructions:** Forbidden actions, escalation triggers, tone & voice, campaign guidelines
- **Location-Specific:** Business context (address, phone, hours, manager names)
- **Implementation:** Copy shared instructions, customize business context per location

**Time Required:** 30 minutes for first location, 10 minutes per additional location

---

## ✅ Success Metrics

### How to know if instructions are working:

**Safety Metrics:**
- ✅ Zero unauthorized refunds or discounts
- ✅ All serious issues escalated appropriately
- ✅ No legal or compliance violations

**Member Satisfaction:**
- ✅ Positive feedback on communication tone
- ✅ Reduced complaints about AI behavior
- ✅ Higher response rates to campaigns

**Operational Efficiency:**
- ✅ Fewer unnecessary escalations
- ✅ More accurate information provided
- ✅ Consistent brand voice across interactions

**Business Performance:**
- ✅ Improved collections success rate
- ✅ Higher campaign conversion rates
- ✅ Increased member retention

---

## 🚀 Next Steps

1. **Read this guide** ✓ You're here!
2. **Choose your path:**
   - Quick setup: Use `AI_INSTRUCTIONS_TEMPLATES.md`
   - Detailed understanding: Read `AI_INSTRUCTIONS_EXAMPLES.md`
   - Fast track: Follow `AI_INSTRUCTIONS_QUICK_START.md`
3. **Customize templates** for your gym
4. **Add to settings** via dashboard
5. **Test** with validation script
6. **Monitor** AI behavior for first week
7. **Refine** based on real interactions
8. **Maintain** regularly

---

**Ready to get started?** Open `docs/AI_INSTRUCTIONS_TEMPLATES.md` and start customizing!
