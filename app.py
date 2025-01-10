import streamlit as st
import json
from pathlib import Path
import time
from typing import Dict, List, Any
import subprocess
from dataclasses import dataclass
from enum import Enum

class TaskStatus(Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"

@dataclass
class ExperimentTask:
    name: str
    status: TaskStatus
    progress: float = 0.0

class BacktestManager:
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.load_experiments()
        
    def load_experiments(self) -> None:
        """Load experiment configuration from file"""
        with open(self.config_path) as f:
            self.experiments = json.load(f)
    
    def run_check(self, experiment_type: str, universe: str, product: str) -> bool:
        """Execute check script for given experiment parameters"""
        try:
            result = subprocess.run(
                ["python", "check_experiment.py", 
                 "--experiment", experiment_type,
                 "--universe", universe,
                 "--product", product],
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            st.error(f"Check failed: {e.stderr}")
            return False

    def run_batch(self, experiment_type: str, universe: str, product: str) -> bool:
        """Execute batch run script for given experiment parameters"""
        try:
            result = subprocess.run(
                ["python", "run_batch.py",
                 "--experiment", experiment_type,
                 "--universe", universe,
                 "--product", product],
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            st.error(f"Batch run failed: {e.stderr}")
            return False

    def summarize(self, experiment_type: str, universe: str, product: str) -> bool:
        """Execute summary script for given experiment parameters"""
        try:
            result = subprocess.run(
                ["python", "summarize.py",
                 "--experiment", experiment_type,
                 "--universe", universe,
                 "--product", product],
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            st.error(f"Summary generation failed: {e.stderr}")
            return False

def create_progress_container():
    """Create a container for the progress bar and status"""
    container = st.empty()
    progress_bar = container.progress(0)
    return container, progress_bar

def create_experiment_ui():
    st.title("Backtest Experiment Manager")
    
    # Initialize session state for tracking task status
    if 'tasks' not in st.session_state:
        st.session_state.tasks = {}

    # Initialize BacktestManager
    manager = BacktestManager("experiments_config.json")
    
    # Create UI for each experiment type
    for exp_type, universes in manager.experiments.items():
        st.header(f"Experiment: {exp_type}")
        
        for universe, products in universes.items():
            st.subheader(f"Universe: {universe}")
            
            for product, frontier_points in products.items():
                st.write(f"Product: {product}")
                col1, col2, col3 = st.columns(3)
                
                # Generate unique keys for each task
                check_key = f"{exp_type}_{universe}_{product}_check"
                batch_key = f"{exp_type}_{universe}_{product}_batch"
                summary_key = f"{exp_type}_{universe}_{product}_summary"
                
                # Initialize task status if not exists
                for key in [check_key, batch_key, summary_key]:
                    if key not in st.session_state.tasks:
                        st.session_state.tasks[key] = ExperimentTask(
                            name=key,
                            status=TaskStatus.NOT_STARTED
                        )

                # CHECK button and progress
                with col1:
                    if st.button("CHECK", key=f"check_btn_{check_key}"):
                        task = st.session_state.tasks[check_key]
                        task.status = TaskStatus.IN_PROGRESS
                        
                        container, progress_bar = create_progress_container()
                        for i in range(100):
                            time.sleep(0.01)  # Simulate work
                            progress_bar.progress(i + 1)
                            task.progress = (i + 1) / 100
                            
                        success = manager.run_check(exp_type, universe, product)
                        task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
                        container.empty()
                    
                    st.write(f"Status: {st.session_state.tasks[check_key].status.value}")

                # BATCH RUN button and progress
                with col2:
                    if st.button("RUN ON BATCH", key=f"batch_btn_{batch_key}"):
                        task = st.session_state.tasks[batch_key]
                        task.status = TaskStatus.IN_PROGRESS
                        
                        container, progress_bar = create_progress_container()
                        for i in range(100):
                            time.sleep(0.01)  # Simulate work
                            progress_bar.progress(i + 1)
                            task.progress = (i + 1) / 100
                            
                        success = manager.run_batch(exp_type, universe, product)
                        task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
                        container.empty()
                    
                    st.write(f"Status: {st.session_state.tasks[batch_key].status.value}")

                # SUMMARIZE button and progress
                with col3:
                    if st.button("SUMMARIZE", key=f"summary_btn_{summary_key}"):
                        task = st.session_state.tasks[summary_key]
                        task.status = TaskStatus.IN_PROGRESS
                        
                        container, progress_bar = create_progress_container()
                        for i in range(100):
                            time.sleep(0.01)  # Simulate work
                            progress_bar.progress(i + 1)
                            task.progress = (i + 1) / 100
                            
                        success = manager.summarize(exp_type, universe, product)
                        task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
                        container.empty()
                    
                    st.write(f"Status: {st.session_state.tasks[summary_key].status.value}")

                st.markdown("---")

if __name__ == "__main__":
    create_experiment_ui()