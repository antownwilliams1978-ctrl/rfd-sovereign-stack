# Two Feather Games & Charity: Complete Platform Architecture
## Entertainment Gaming + Sweepstakes Prize Model

---

## EXECUTIVE SUMMARY

**Platform Model**: Players purchase GC, receive minimal SC as gift, play games, win real prizes from SC gameplay only.

- **GC (Gaming Coins)**: Purchased with real money, entertainment-only (no withdrawal)
- **SC (Social Coins)**: Minimal automatic gift when buying GC ($30K GC = 20 SC), must be played through before redemption
- **Prizes**: Real USD/gift cards won by playing with SC (1:1 ratio for winnings >50 SC)
- **Charity**: 60% of GC revenue + 100% of partner 70/30 split goes to nonprofit

---

## SECTION 1: CURRENCY SYSTEM

### 1.1 Gaming Coins (GC)

**Purpose**: Entertainment play currency

**Acquisition**:
- Purchase: $4.99, $9.99, $24.99, $49.99, $99.99 packs
- Buy $30,000 GC → **Automatically receive 20 SC as a gift** (1:1500 ratio, ~0.067%)
- First-time player bonus: Buy $4.99 → Get $9.98 GC (2x bonus, no extra SC)

**Usage**:
- Wager on any game (proprietary or partner)
- No withdrawal
- No prize redemption
- Expires if account inactive for 180 days

**Mechanics**:
- Win = GC stays in account for re-play
- Lose = GC spent, gone
- No accumulation of "real value"

**Legal Stance**: "Entertainment chips — like a Vegas slot machine. Fun, but not real money."

**Conversion Rate (GC to SC Gift)**:
```
$4.99 GC → 0 SC (rounding: <1 SC)
$9.99 GC → 0 SC (rounding: <1 SC)
$24.99 GC → 0 SC (rounding: ~0.017 SC)
$49.99 GC → 0 SC (rounding: ~0.033 SC)
$99.99 GC → 0 SC (rounding: ~0.067 SC, rounds to 0)
$300 GC → 0 SC (rounds to 0)
$30,000 GC → 20 SC (triggers first SC gift)
```

---

### 1.2 Social Coins (SC)

**Purpose**: Prize-earning currency via gameplay only

**Acquisition**:
- **Primary**: Automatic gift when purchasing GC (1:1500 ratio)
  - $30,000 GC purchase → 20 SC gift
  - $150,000 GC purchase → 100 SC gift
- **Secondary**: Won through gameplay only
  - Win $50+ SC in games = eligible for redemption
- **Tertiary**: Rare event bonuses (after play-through req met)

**Play-Through Requirement** (MUST be completed before prize redemption):
- All gifted SC **must be wagered in games** before any redemption is allowed
- System tracks: "Gift SC Status" (Pending Play-Through | Completed | Redeemable)
- Player cannot redeem prizes until gift SC is spent/wagered
- Example: Receive 20 SC gift → Play games with 20 SC → Once wagered/spent → Now eligible for prize redemption

**Usage**:
- Wager on any game (proprietary or partner)
- **Wins are real**: SC winnings (>50 SC) convert to actual USD/gift cards at 1:1 ratio
- No expiration (permanent gift once play-through complete)
- Can re-wager winnings

**Mechanics**:
- Gift SC: Must be played through before redemption eligibility
- Winnings (>50 SC): Redeem for $1:1 USD value
- Winnings (<50 SC): Can only re-play, not redeem

**Legal Stance**: "Minimal free gift with GC purchase. Gift must be played through. Wins are real prizes earned through entertainment."

---

### 1.3 Prize Redemption Rules

**Redemption Eligibility**:
1. ✅ Play-through requirement completed (gift SC wagered)
2. ✅ SC winnings from gameplay **above 50 SC threshold**
3. ✅ Player verified (ID for redemptions >$600/year)

**Available Redemptions** (1:1 SC to USD):
- USD via PayPal (minimum $50, equal to $50 SC)
- Gift cards: Starbucks, Amazon, Best Buy, DoorDash, etc. ($50-$1,000)
- Prepaid debit cards (via partner processor)
- Donate back to nonprofit (generates tax receipt)

**Redemption Tiers**:
```
SC Winnings → Prize Redemption (1:1 Ratio)
0-50 SC win   → Cannot redeem (play-only)
51-200 SC     → Redeem as $51-200 (verification not required)
201-600 SC    → Redeem as $201-600 (light ID check)
601+ SC       → Redeem as $601+ (full ID verification required, 1099 issued)
```

**Prize Pool Funding**:
- 40% of GC revenue reserved for prize redemption
- Example: $10,000 GC revenue/month → $4,000 prize pool
- Ensures sustainability (SC winnings come from house edge)

**Redemption Process**:
1. Player accumulates >50 SC from wins
2. Clicks "Redeem Prize"
3. Selects prize type and amount
4. Completes verification (if applicable)
5. Prize delivered within 3-5 business days
6. Tax receipt auto-generated (1099-MISC for >$600/year)

---

## SECTION 2: GAME ARCHITECTURE

### 2.1 Game Categories (50 Total)

#### **A. PROPRIETARY GAMES (30 games — 100% to charity)**

**Slot Engine A: Wild Multiplier (6 games)**
- `RedFeatherWild` — 5-reel, 1-3 random wilds/spin, 1-5x multiplier
- `BuffaloSpin` — 5-reel, expanding wild, re-spins
- `EagleSkyWild` — 5-reel, roaming wild, moving left/right
- `SacredWildExpand` — 5-reel, expanding wild on all reels
- `CouncilWildMult` — 5-reel, stacked wild, chain multiplier
- `RiverWild` — 5-reel, wild substitute + bonus coins

**Slot Engine B: Free Spin Scatter (6 games)**
- `TwoFeatherBonus` — 5-reel, 3+ scatter = 12 free spins, 2x multiplier
- `FeatherScatterSpins` — 5-reel, retriggerable free spins
- `CouncilBonusSpins` — 5-reel, progressive multiplier free spins
- `AncestralBonus` — 5-reel, 10-20 free spins, random coin boosts
- `FireCircleBonus` — 5-reel, mystery multiplier free spins
- `TradeRouteBonus` — 5-reel, cascading bonus feature

**Slot Engine C: Cascading/Cluster (3 games)**
- `FeatherCascade` — Vertical cascade, 5 in a row = win
- `RiverStoneCluster` — 5x3 cluster mechanic, expanding wilds
- `GoldRushCascade` — Horizontal cascades, unlimited re-spins

**Slot Engine D: Mega Symbol (3 games)**
- `ColosalEagle` — 4x4 mega eagle, instant 2x payout
- `MegaBuffalo` — 3x3 mega buffalo symbols, wild substitute
- `GoldenCouncil` — 2x2 golden symbols, bonus trigger

**Instant-Win Games (8 games)**
- **Card Reveal**: `LuckyPennyFlip` (pick 5, win all), `FeatherReveal` (9-card grid)
- **Wheel Spin**: `FeatherWheel` (spin for 1-10x multiplier), `SacredSpinner` (bonus wheel)
- **Match**: `FeatherMatch` (match 3 of 5), `RiverMatch` (animated stone match)
- **Dice**: `CouncilDice` (roll 3 dice, sum multiplier), `TradeNumber` (pick 5 numbers)

**Table/Card Games (4 games)**
- **Blackjack**: `FeatherBlackjack` (single hand), `CouncilCards` (multi-hand)
- **Poker**: `SacredPoker` (5-card draw), `FeatherHand` (video poker, Jacks or better)

---

#### **B. PARTNER GAMES (20 games — 70/30 split)**

**Partner Studio 1: "Constellation Games"** (8 games)
- `Mystic Fortune` (5-reel wild multiplier)
- `Dragon Dynasty` (5-reel expanding wilds)
- `Phoenix Rising` (5-reel cascade)
- `Celestial Luck` (instant-win card reveal)
- `Starlight Spin` (instant-win wheel)
- `Astral Blackjack` (table: 1/2 hand)
- `Cosmic Poker` (table: video poker)
- `Constellation Match` (instant-win match 3)

**Partner Studio 2: "Sacred Lands"** (7 games)
- `Mountain Peak` (5-reel scatter bonus)
- `Forest Quest` (5-reel free spins)
- `Desert Gold` (5-reel mega symbols)
- `Woodland Luck` (instant-win pick game)
- `Sacred Spin` (instant-win wheel variant)
- `Nature's Hand` (table: poker)
- `Wilderness Roulette` (table: social roulette)

**Partner Studio 3: "Fortune Labs"** (5 games)
- `Golden Age` (5-reel wild multiplier)
- `Lucky Token` (instant-win token match)
- `Fortune Wheel Deluxe` (instant-win enhanced wheel)
- `Jackpot Bluff` (table: poker with raises)
- `Classic Blackjack Pro` (table: multi-hand)

---

### 2.2 Game Mechanics & Compliance

**All games enforce**:
- ✅ Track SC separately: Gift SC (must play-through) vs Won SC (redeemable)
- ✅ No cash references ("earn," "win," "collect" only)
- ✅ No payout promises (language: "potential prize," "if lucky")
- ✅ No "real money" language (use "social coins," "donations")
- ✅ All outcomes must be clear (RNG seed logged for disputes)
- ✅ House edge transparent: "Average return 92% (GC), 94% (SC)"
- ✅ Display: "Prize redemption available for winnings >50 SC"

**House Edge Model**:
- **GC games**: 8% average house edge (entertainment)
- **SC games**: 6% average house edge (incentive to play minimal gift)
- Difference funds prize pool + nonprofit operations

**Play-Through Tracking**:
- System logs: All gift SC must be "wagered" in games
- Wager = any spin/hand played with gift SC
- Once wager total ≥ gift SC amount → Play-through complete
- Automatic unlock: "Now eligible for prize redemption"

---

## SECTION 3: REVENUE MODEL

### 3.1 GC Purchase Revenue Stream

**Monthly GC Sales (Projection)**:
- $100 avg player × 1,000 active players = $100,000/month

**GC Revenue Distribution**:

```
GC Purchase Revenue: $100,000/month
├─ Prize Pool (40%): $40,000
│  └─ Funded by house edge (SC winnings >50, redeemed 1:1)
├─ Two Feathers Nationals (50%): $50,000
│  └─ Nonprofit operations, programs, board decisions
├─ Platform Ops (10%): $10,000
│  └─ Server costs, payment processing, support staff
```

**Explanation**:
- Players pay $100K for GC (entertainment, not returnable)
- Players receive $67 SC (at 1:1500 ratio for $100K in GC) — minimal gift
- Prize pool ($40K) comes from house edge on SC games
- Charity gets 50% of GC revenue (core mission funding)
- Ops costs are minimal (headless architecture on Vultr)

---

### 3.2 Partner Revenue Stream

**Partner Game Sales** (estimated 30% of total GC volume from partner games):
- $100,000 total GC × 30% = $30,000 partner game revenue/month

**Partner Split**:
```
Partner Game Revenue: $30,000/month
├─ Partner Studio: $9,000 (30%)
└─ Two Feathers Nationals: $21,000 (70%)
```

**Total charity revenue from GC**: $50,000 (direct) + $21,000 (partner) = **$71,000/month**

---

### 3.3 Donation Revenue (Optional, Separate)

**Donation Processing**:
- Average donation: $25 USD
- Platform fee: 2.2% + $0.30 (via Stripe)
- Nonprofit receives: $24.46 per $25 donation
- Donor receives: SC bonus (optional) + tax-deductible receipt

**Projected Donation Volume**:
- 5-10% of active players donate monthly (conservative)
- 1,000 players × 7.5% = 75 donations/month
- 75 × $25 avg = $1,875/month gross
- 75 × $24.46 net = $1,835/month to nonprofit

**Total monthly charity revenue**:
- GC-based: $71,000
- Donations: $1,835
- **Total: $72,835/month**

---

## SECTION 4: LEGAL COMPLIANCE FRAMEWORK

### 4.1 Why This Is NOT Gambling

**Definition of Gambling**: Exchange real money for a chance to win based on chance or skill, where outcome is random and result is uncertain.

**How RFD Avoids Gambling Classification**:

| Element | Traditional Gambling | RFD Model |
|---------|---|---|
| **GC Purchase** | Wager (money at risk) | Purchase for entertainment (no refund) |
| **SC Acquisition** | N/A | Negligible gift (1:1500 ratio, ~$0.067 per $100 spent) |
| **Play with GC** | Using wagered money | Using purchased entertainment currency |
| **Play with SC** | N/A | Using free minimal gift (must play-through first) |
| **Outcome** | Win = cash payout from wager | Win = prize from separate pool (only >50 SC) |
| **Consideration** | Player pays to play | No payment for SC play (it's a gift) |
| **Real Value Risk** | Entire bet at risk | SC gift has no cash value; plays through before redemption |

**Legal Theory**: This is a **sweepstakes**, not gambling:
- Entry with SC is free (it's a minimal gift)
- Entry requires play-through (gift must be wagered)
- Outcome is random (RNG-based)
- Prizes are real (funded separately, only for winners >50 SC)
- No consideration of payment for SC entry

**Key Regulatory Quote** (FTC):
> "Sweepstakes require no consideration for entry and random chance determines winners."

**SC Play Defense**: "Players receive negligible SC (~0.067 per $100 GC) as a free gift. Before any prize redemption is allowed, this gift must be played through in games. Only winners accumulating >50 SC can redeem prizes. This is a classic sweepstakes: free entry, random outcome, real prizes."

---

### 4.2 Firewall Requirements

**Charitable Donation System**:
- ✅ Separate legal entity: Two Feathers Nationals (nonprofit)
- ✅ Separate bank account (no commingling)
- ✅ Donation processor: Stripe Nonprofit or PayPal Giving Fund
- ✅ Tax receipts issued by nonprofit, not platform
- ✅ Annual 990-N filing (nonprofit transparency)

**Game System**:
- ✅ Platform (Two Feather Games LLC) separate from nonprofit
- ✅ No donation language inside games
- ✅ No game outcomes tied to donation matching
- ✅ Prize pool funded from GC revenue/house edge (traceable ledger)
- ✅ SC tracked separately: Gift (play-through) vs Won (redeemable)

**Prize System**:
- ✅ Prize payouts from dedicated fund, not player deposits
- ✅ Prize redemption only for SC winnings >50
- ✅ 1099 issued for prizes >$600/year
- ✅ Prize policy published (RTG — Return to Player)
- ✅ Appeals process for disputed outcomes

---

### 4.3 State-by-State Considerations

**Most US States**: Social gaming is legal (subject to state definitions)

**Problem States**:
- **Washington**: Social gaming with prizes may require license
- **Illinois**: Prize redemptions may need approval
- **New York**: Skill-based game licensing possible

**Strategy**: 
- Launch as "invite-only private beta" in all states
- Obtain legal review in target states before public launch
- Implement geofencing for restricted states
- Have 501(c)(3) approval letter from IRS as defense
- Document that SC is negligible and requires play-through before redemption

---

## SECTION 5: IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Weeks 1-4)
- [ ] Build core slot engine framework (reusable codebase)
- [ ] Implement RNG + fairness auditing
- [ ] Create Stripe integration for GC purchases
- [ ] **Build dual SC wallet system** (Gift SC + Won SC tracking)
- [ ] **Implement play-through tracking** (gift SC must be wagered)
- [ ] Create user authentication + KYC for >$600 prizes

**Deliverables**:
- Working slot engine running locally
- Payment processor integration
- Dual SC wallet with play-through requirement
- User account system with wallet displays

---

### Phase 2: Proprietary Games (Weeks 5-8)
- [ ] Deploy 18 proprietary slot games
- [ ] Deploy 8 instant-win games
- [ ] Deploy 4 table/card games
- [ ] Create game library UI (category filters, search)
- [ ] **Implement SC redemption system** (>50 SC threshold)

**Deliverables**:
- 30 playable games in private beta
- Prize redemption workflow end-to-end
- Admin dashboard for game management

---

### Phase 3: Charity Integration (Weeks 9-10)
- [ ] Set up Two Feathers Nationals nonprofit entity (Inc + EIN)
- [ ] Open nonprofit bank account
- [ ] Integrate donation processor (Stripe Nonprofit)
- [ ] Build donation UI (separate from SC gifting)
- [ ] Create Impact Center (nonprofit mission display)

**Deliverables**:
- Donation button working (optional, separate)
- Nonprofit transparency page
- SC gifting working automatically on all GC purchases

---

### Phase 4: Partner Onboarding (Weeks 11-14)
- [ ] Create partner portal (game submission + rev-share tracking)
- [ ] Integrate first partner studio (8 games)
- [ ] Implement 70/30 revenue settlement + reporting
- [ ] Build partner compliance checklist + audit trail
- [ ] Deploy second and third partners

**Deliverables**:
- 20 partner games live
- Revenue split tracking
- Partner dashboard (their revenue visibility)

---

### Phase 5: Launch & Scale (Weeks 15-16)
- [ ] Full compliance audit (legal review)
- [ ] Load testing (1,000+ concurrent players)
- [ ] Public beta launch (invite-only)
- [ ] Community building + social features
- [ ] Analytics + engagement optimization

**Deliverables**:
- Live public beta
- 50 games fully operational
- Revenue settlement system running

---

## SECTION 6: COMPETITIVE DIFFERENTIATION

| Aspect | High5 Casino | Crown Coin | **Two Feather Games** |
|--------|---|---|---|
| **Games** | 100+ (generic) | 80+ (generic) | 50 (curated, cultural) |
| **Currency Model** | VIP tier (whales) | Whale focus | 2-tier (GC/SC) |
| **SC Gift Model** | None | None | **Minimal gift + play-through** |
| **Prize Threshold** | All wins | Limited | >50 SC only |
| **Charity** | None | None | 60%+ revenue |
| **Prize Model** | No real prizes | Limited | Real USD/gift cards |
| **Donation Incentive** | None | None | Free SC + tax deduction |
| **Transparency** | Opaque | Opaque | Full audit trail |
| **Cultural Identity** | None | None | Indigenous-rooted |

---

## SECTION 7: RISK MITIGATION

### Legal Risks

**Risk**: State considers SC play "gambling"
**Mitigation**: 
- Keep SC gifting completely separate from purchase confirmation
- Use language: "You received a negligible free gift currency, not purchased it"
- Document that SC gift must be played through before any redemption
- Document that only winners >50 SC can redeem (rest play-only)
- Have nonprofit issue receipts for donations, platform for GC purchases
- Obtain legal opinion in target states

**Risk**: IRS challenges 501(c)(3) nonprofit status
**Mitigation**:
- 990-N filing annual (transparency)
- No excessive compensation to board
- Charity does actual community work (fund programs)
- Keep nonprofit separate from gaming LLC

---

### Financial Risks

**Risk**: Prize payouts exceed GC revenue
**Mitigation**:
- Set house edge conservatively (8-10%)
- Monitor RTG (Return to Player) monthly
- Only award prizes from house edge (not from player deposits)
- Maintain 3-month reserve fund

**Risk**: Players game the play-through system
**Mitigation**:
- Track all wagers with gift SC (system immutable log)
- Cannot redeem until play-through complete (system enforced)
- Cannot accumulate gift SC repeatedly (one-time per purchase)
- Monitor for multi-accounting abuse

---

### Operational Risks

**Risk**: Partner games contain non-compliant language
**Mitigation**:
- Mandatory compliance review before launch
- Weekly code audit of partner games
- Automatic de-listing if violations found
- Clear contract: "Partner liable for compliance violations"

---

## SECTION 8: NEXT ACTIONS

**Immediate** (This Week):
- [ ] Consult gaming attorney re: sweepstakes classification (emphasize play-through + high threshold)
- [ ] File nonprofit articles of incorporation for Two Feathers Nationals
- [ ] Set up Stripe Nonprofit account for donation processing
- [ ] Create detailed game specification for Slot Engine A

**Short-term** (Next 2 weeks):
- [ ] Build core slot engine framework (code)
- [ ] Create user authentication system
- [ ] Integrate Stripe for GC purchases + **SC gifting (1:1500 ratio)**
- [ ] **Build play-through tracking system**
- [ ] Begin development on 6 Slot Engine A games

**Medium-term** (Weeks 3-4):
- [ ] Integrate donation processor (separate from SC gifting)
- [ ] Build dual wallet system (Gift SC | Won SC)
- [ ] **Create 50 SC redemption threshold logic**
- [ ] Deploy first 6 games to private beta

---

## APPENDIX: Currency Conversion Chart

```
Real Money → GC Purchase (No Prize Conversion on GC)
$4.99 GC → 0 SC (gift rounds to 0)
$9.99 GC → 0 SC (gift rounds to 0)
$24.99 GC → 0 SC (gift rounds to 0)
$49.99 GC → 0 SC (gift rounds to 0)
$99.99 GC → 0 SC (gift rounds to 0)
$300 GC → 0 SC (gift rounds to 0)
$30,000 GC → 20 SC gift (1:1500 ratio)
$150,000 GC → 100 SC gift (1:1500 ratio)

Optional Real Money → SC (Donation Route)
$10 Donation → 10,000 SC bonus (gift) + tax receipt
$25 Donation → 25,000 SC bonus (gift) + tax receipt
$50 Donation → 50,000 SC bonus (gift) + tax receipt
$100 Donation → 100,000 SC bonus (gift) + tax receipt

SC Gameplay → Prize Redemption (1:1 Ratio, >50 SC Only)
Winnings 0-50 SC   → Cannot redeem (play-only)
Winnings 51-200 SC → Redeem as $51-200 prize
Winnings 201+ SC   → Redeem as $201+ prize (ID verification required)

Example Player Journey:
1. Buy $30,000 GC → Receive 20 SC gift
2. Play games with 20 SC gift (must wager all first)
3. Win 150 SC from gameplay (now have 150 SC eligible)
4. Play-through complete: Gift SC exhausted
5. Redeem 100 SC as $100 PayPal (>50 threshold met)
6. Can keep playing with remaining 50 SC (sub-threshold, play-only)
```

---

**This model is sustainable, legally defensible, and charity-centric. Let's build it.**
