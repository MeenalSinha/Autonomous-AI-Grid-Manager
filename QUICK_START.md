# Quick Start Guide - Get Running in 5 Minutes

## Prerequisites
- Python 3.8+ installed
- Internet connection (for installing packages)
- Terminal/Command Prompt access

## Installation Steps

### 1. Install Python Dependencies

#### Option A: Using the run script (Recommended for Linux/Mac)
```bash
chmod +x run.sh
./run.sh
```

#### Option B: Manual installation
```bash
pip install streamlit numpy pandas plotly torch
```

or 

```bash
pip install -r requirements.txt
```

### 2. Start the Application

```bash
streamlit run app.py
```

The browser will automatically open to `http://localhost:8501`

If it doesn't open automatically, manually navigate to: `http://localhost:8501`

## First-Time Setup (In the App)

1. **Train the AI Agent**
   - Click the sidebar on the left
   - Find "AI Training" section
   - Click "🚀 Train RL Agent (Quick)"
   - Wait ~30 seconds for training to complete
   - You'll see "✅ Agent Trained" when done

2. **Start the Simulation**
   - Click "▶️ Start" button in sidebar
   - Watch the real-time graphs update
   - Observe the AI making decisions

3. **Try Stress Testing**
   - Click any of the stress test buttons:
     - ☁️ Cloud Cover
     - 💨 Wind Drop
     - 📈 Peak Demand
     - 🔋 Battery Degradation
   - Watch how the AI responds in real-time

4. **Compare AI vs Rule-Based**
   - Click "Reset Simulation"
   - Enable "Run Side-by-Side Comparison" checkbox
   - Click "Start" again
   - Inject same events and compare performance

## Troubleshooting

### Port Already in Use
If you see "Address already in use" error:
```bash
streamlit run app.py --server.port 8502
```

### Package Installation Issues
If pip install fails, try:
```bash
pip install --user streamlit numpy pandas plotly torch
```

or with Python 3 explicitly:
```bash
python3 -m pip install streamlit numpy pandas plotly torch
```

### Import Errors
Make sure you're in the correct directory:
```bash
cd path/to/autonomous-ai-grid-manager
python3 -c "import streamlit; print('✅ Streamlit OK')"
```

### Torch Installation (CPU-only)
If you don't need GPU support and torch install is slow:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

## What to Expect

When the app starts successfully, you should see:
- ⚡ Large header "Autonomous AI Grid Manager"
- Sidebar with controls on the left
- Four metric cards at the top (Grid Stability, Battery SOC, Renewable %, Energy Cost)
- Real-time graphs in the main area
- Statistics summary at the bottom

## Quick Demo Flow

**For a 2-minute demo:**

1. Start app
2. Train AI (30 seconds)
3. Start simulation
4. Inject "Cloud Cover" event
5. Show AI maintaining stability
6. Point to cost savings metrics

**For a 5-minute demo:**

1. Start app
2. Train AI
3. Enable comparison mode
4. Start simulation
5. Inject multiple events (cloud, wind, demand)
6. Show side-by-side AI vs Rule-based performance
7. Highlight improvement percentages
8. Show decision log explainability

## Demo Tips

- **Internet Speed**: All computations are local, no internet needed after install
- **Browser**: Works best in Chrome or Firefox
- **Screen Size**: Use fullscreen for best viewing experience
- **Performance**: Simulation runs smoothly on any modern laptop

## Common Questions

**Q: How long does training take?**
A: ~30 seconds for quick training. Longer training (5+ minutes) gives better results but isn't necessary for demos.

**Q: Can I pause and resume?**
A: Yes, use the ⏸️ Pause button. The simulation state is preserved.

**Q: What if the AI performs poorly?**
A: Click "Retrain" to reset and train again. Random initialization can affect initial performance.

**Q: Can I export the data?**
A: Currently shows real-time only. Export functionality can be added (see code comments in app.py).

## File Structure

```
.
├── app.py                 # Main Streamlit application
├── grid_simulator.py      # Grid physics and dynamics
├── rl_agent.py           # RL algorithms (PPO, DQN, SAC)
├── forecaster.py         # LSTM forecasting
├── requirements.txt      # Python dependencies
├── README.md            # Full documentation
├── DEMO_SCRIPT.md       # Presentation script
├── QUICK_START.md       # This file
└── run.sh              # Startup script (Linux/Mac)
```

## Next Steps

After getting it running:
1. Read `DEMO_SCRIPT.md` for presentation tips
2. Review `README.md` for technical details
3. Experiment with different scenarios
4. Try comparing different RL algorithms (in code)
5. Adjust simulation parameters for your use case

## Support

If you encounter issues:
1. Check Python version: `python3 --version` (should be 3.8+)
2. Verify packages: `pip list | grep -E "streamlit|torch|plotly"`
3. Check terminal for error messages
4. Ensure you're in the correct directory

## Success Indicators

You've successfully set up when you can:
- ✅ See the dashboard in browser
- ✅ Train the AI agent
- ✅ Run the simulation
- ✅ Inject stress events
- ✅ See metrics updating in real-time
- ✅ Compare AI vs Rule-based performance

---

**Ready to demo? You're all set! 🚀**

Open the app, train the AI, and start showing how autonomous intelligence can stabilize renewable energy grids.
