# 🧪 Runtime Testing Checklist

## ✅ Pre-Demo Testing Guide

This checklist ensures your application runs flawlessly during the demo. Test each scenario before presenting to judges.

---

## 🎯 Critical Tests (Must Complete)

### Test 1: Basic Simulation ✓
**Objective:** Verify single-mode simulation works without errors

**Steps:**
1. Start application: `streamlit run app.py`
2. Click "Train RL Agent (Quick)" 
3. Wait for training to complete (~30 seconds)
4. Click "▶️ Start" button
5. Let simulation run for 50-100 steps
6. Click "⏸️ Pause" button
7. Verify no errors in console

**Expected Result:**
- ✅ Training completes without errors
- ✅ Simulation runs smoothly
- ✅ Graphs update in real-time
- ✅ Metrics display correctly
- ✅ Pause stops simulation
- ✅ No `st.rerun()` infinite loops

**Pass Criteria:**
- No Python errors
- No browser freezing
- Clean pause/resume behavior

---

### Test 2: Comparison Mode (CRITICAL) ✓
**Objective:** Verify AI vs Legacy comparison works end-to-end

**Steps:**
1. Reset simulation (click "🔄 Reset Simulation")
2. Train AI agent again
3. Enable "Run Side-by-Side Comparison" checkbox
4. Click "▶️ Start"
5. Let both simulators run for 50-100 steps
6. Watch performance banner populate
7. Verify both simulators progress together
8. Click "⏸️ Pause"

**Expected Result:**
- ✅ Both simulators start simultaneously
- ✅ Performance banner shows 4 metrics
- ✅ AI and Legacy graphs display side-by-side
- ✅ No naming errors (simulator_legacy vs simulator_rule)
- ✅ Comparison statistics display correctly
- ✅ No infinite loops

**Pass Criteria:**
- Both simulators run in parallel
- No `AttributeError` or `KeyError`
- Performance metrics calculate correctly
- Clean pause behavior

---

### Test 3: Stress Testing ✓
**Objective:** Verify event injection doesn't crash

**Steps:**
1. Start simulation (single or comparison mode)
2. Let run for 20 steps
3. Click "☁️ Cloud Cover"
4. Observe AI response
5. Wait 10 steps
6. Click "💨 Wind Drop"
7. Wait 10 steps
8. Click "📈 Peak Demand"
9. Wait 10 steps
10. Click "🔋 Battery Degradation"

**Expected Result:**
- ✅ Each event triggers immediately
- ✅ Grid state changes reflect event
- ✅ AI responds to each event
- ✅ No crashes or errors
- ✅ Simulation continues smoothly

**Pass Criteria:**
- All 4 event types work
- No crashes on event injection
- AI shows adaptive behavior

---

### Test 4: Infinite Loop Protection ✓
**Objective:** Verify max steps safety limit works

**Steps:**
1. Start simulation
2. Set speed slider to 10 (maximum)
3. Let simulation run unattended
4. Wait for max steps (1000) to be reached

**Expected Result:**
- ✅ Simulation stops at 1000 steps
- ✅ Warning message displays
- ✅ No infinite loop occurs
- ✅ Can reset and continue

**Pass Criteria:**
- Automatic stop at max steps
- Warning message appears
- No browser freeze

---

### Test 5: Predictive Mode Toggle ✓
**Objective:** Verify LSTM forecasting integration

**Steps:**
1. Reset simulation
2. Train AI agent
3. Enable "Use LSTM Forecasting" toggle
4. Start simulation
5. Let run for 50 steps (to populate forecaster)
6. Verify "🔮 Using LSTM Forecasts" shows in AI insights
7. Disable forecasting toggle
8. Reset and start again
9. Verify "⚡ Reactive Control" shows

**Expected Result:**
- ✅ Toggle switches between 10D and 13D states
- ✅ Forecaster buffer populates
- ✅ AI insights reflect current mode
- ✅ No errors switching modes

**Pass Criteria:**
- Both modes work
- State dimension changes correctly
- No crashes on toggle

---

### Test 6: UI Responsiveness ✓
**Objective:** Verify glassmorphism UI renders correctly

**Steps:**
1. Open app in browser
2. Check hero section displays
3. Verify all glass cards load
4. Hover over metric cards (should lift)
5. Hover over buttons (should lift)
6. Check animations (logo bounce, fade-ins)
7. Scroll to footer
8. Verify tech badges display

**Expected Result:**
- ✅ Hero section with bouncing logo
- ✅ Glass cards with blur effect
- ✅ Hover animations work
- ✅ Gradient backgrounds display
- ✅ Footer renders correctly

**Pass Criteria:**
- All CSS loads correctly
- Animations smooth (60fps)
- No visual glitches

---

## 🔍 Edge Case Tests (Recommended)

### Test 7: Rapid Toggle Switching
**Steps:**
1. Rapidly toggle "AI Autonomous Control" on/off 10 times
2. Rapidly toggle "Use LSTM Forecasting" on/off 10 times
3. Verify no state corruption

**Expected:** No errors, clean state updates

---

### Test 8: Multiple Simultaneous Events
**Steps:**
1. Start simulation
2. Click all 4 stress test buttons within 5 seconds
3. Verify AI handles multiple concurrent events

**Expected:** AI adapts without crashing

---

### Test 9: Reset During Simulation
**Steps:**
1. Start simulation
2. Let run for 30 steps
3. Click "🔄 Reset Simulation" while running
4. Verify clean reset

**Expected:** Simulation stops, state resets, no errors

---

### Test 10: Browser Refresh
**Steps:**
1. Start simulation
2. Refresh browser (F5)
3. Verify app restarts cleanly

**Expected:** Fresh session state, no residual errors

---

## 🐛 Common Issues & Solutions

### Issue 1: "simulator_rule not found"
**Cause:** Old naming convention
**Fix:** Already fixed - uses `simulator_legacy` now
**Verify:** Run comparison mode, no AttributeError

---

### Issue 2: Infinite rerun loop
**Cause:** Missing max steps check
**Fix:** Already implemented - 1000 step limit
**Verify:** Let simulation run to limit, should auto-stop

---

### Issue 3: LSTM forecaster errors
**Cause:** Insufficient history buffer
**Fix:** Forecaster has fallback logic
**Verify:** Start simulation with forecasting ON, should work from step 1

---

### Issue 4: Performance banner shows NaN
**Cause:** Insufficient data for comparison
**Fix:** Banner only shows after 30 steps
**Verify:** Wait for 30+ steps in comparison mode

---

### Issue 5: Graphs not updating
**Cause:** Missing st.rerun() or paused simulation
**Fix:** Check simulation is running, speed > 0
**Verify:** Play button pressed, speed slider > 1

---

## ✅ Pre-Demo Final Checklist

**30 Minutes Before Demo:**
- [ ] Close all other applications
- [ ] Clear browser cache
- [ ] Run Test 1 (Basic Simulation)
- [ ] Run Test 2 (Comparison Mode) - CRITICAL
- [ ] Run Test 3 (Stress Testing)
- [ ] Check internet connection (not required but good for stability)
- [ ] Have backup browser open (Chrome + Firefox)

**5 Minutes Before Demo:**
- [ ] Fresh app start: `streamlit run app.py`
- [ ] Verify hero section loads
- [ ] Train AI agent once (confirm it works)
- [ ] Reset simulation to clean state
- [ ] Close dev tools / console
- [ ] Full screen browser window

**During Demo:**
- [ ] Keep calm if minor glitch occurs
- [ ] Have "Reset" button ready
- [ ] Know where "Pause" button is
- [ ] Don't rush through stress tests
- [ ] Let metrics populate before moving on

---

## 🎯 Test Results Template

Copy this and fill it out after testing:

```
=== RUNTIME TEST RESULTS ===

Test 1: Basic Simulation
Status: [ PASS / FAIL ]
Notes: _______________________

Test 2: Comparison Mode
Status: [ PASS / FAIL ]
Notes: _______________________

Test 3: Stress Testing
Status: [ PASS / FAIL ]
Notes: _______________________

Test 4: Infinite Loop Protection
Status: [ PASS / FAIL ]
Notes: _______________________

Test 5: Predictive Mode Toggle
Status: [ PASS / FAIL ]
Notes: _______________________

Test 6: UI Responsiveness
Status: [ PASS / FAIL ]
Notes: _______________________

=== OVERALL READINESS ===
[ ] All critical tests passed
[ ] No infinite loops detected
[ ] Comparison mode works perfectly
[ ] UI renders correctly
[ ] Ready for demo

Tested by: ______________
Date: ______________
Browser: ______________
Python version: ______________
```

---

## 🚨 Emergency Procedures

### If App Crashes During Demo:
1. Stay calm - say "Let me restart that"
2. Hit Ctrl+C in terminal
3. Run: `streamlit run app.py`
4. Train AI again
5. Continue from where you left off

### If Infinite Loop Occurs:
1. Should auto-stop at 1000 steps (already protected)
2. If not, click Pause button
3. Click Reset Simulation
4. Explain: "Safety limit kicked in"

### If Comparison Mode Errors:
1. Disable comparison mode
2. Reset simulation
3. Continue with single-mode demo
4. Still shows all AI features

---

## 💡 Pro Tips

**Tip 1:** Test comparison mode at least 3 times before demo
**Tip 2:** Know your reset button location by muscle memory
**Tip 3:** If nervous, disable comparison mode and do single-mode demo
**Tip 4:** Speed slider at 2-3 is optimal for demos (not too fast/slow)
**Tip 5:** Let AI insights populate for 50+ steps before showing

---

## ✅ Sign-Off

Once all critical tests pass, you're ready to demo.

**Critical Tests (Must Pass):**
- ✅ Test 1: Basic Simulation
- ✅ Test 2: Comparison Mode
- ✅ Test 3: Stress Testing

**Recommended Tests:**
- ✅ Test 4: Infinite Loop Protection
- ✅ Test 5: Predictive Mode Toggle
- ✅ Test 6: UI Responsiveness

**When all critical tests pass: YOU ARE DEMO-READY** 🎯

---

**Remember:** The app is already production-ready. This testing is just to build confidence and muscle memory for the demo. You've got this! 🏆
