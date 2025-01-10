import streamlit as st
import json
from pathlib import Path
import time
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Any

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
        with open(self.config_path) as f:
            self.experiments = json.load(f)
    
    def run_check(self, experiment_type: str, universe: str, product: str) -> bool:
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

def create_experiment_ui():
    st.title("Backtest Experiment Manager")
    
    if 'tasks' not in st.session_state:
        st.session_state.tasks = {}

    try:
        manager = BacktestManager("experiments_config.json")
    except FileNotFoundError:
        st.error("experiments_config.json not found. Please create the configuration file.")
        return
    
    for exp_type, universes in manager.experiments.items():
        st.header(f"Experiment: {exp_type}")
        
        for universe, products in universes.items():
            st.subheader(f"Universe: {universe}")
            
            for product, frontier_points in products.items():
                st.write(f"Product: {product}")
                
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

                # Create columns using beta_columns for 1.12.0
                col1, col2, col3 = st.beta_columns(3)

                # CHECK button
                with col1:
                    task = st.session_state.tasks[check_key]
                    if st.button("CHECK", key=f"check_btn_{check_key}"):
                        task.status = TaskStatus.IN_PROGRESS
                        my_bar = st.progress(0)
                        for percent_complete in range(100):
                            time.sleep(0.01)
                            my_bar.progress(percent_complete + 1)
                        success = manager.run_check(exp_type, universe, product)
                        task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
                    st.text(f"Status: {task.status.value}")

                # BATCH RUN button
                with col2:
                    task = st.session_state.tasks[batch_key]
                    if st.button("RUN ON BATCH", key=f"batch_btn_{batch_key}"):
                        task.status = TaskStatus.IN_PROGRESS
                        my_bar = st.progress(0)
                        for percent_complete in range(100):
                            time.sleep(0.01)
                            my_bar.progress(percent_complete + 1)
                        success = manager.run_batch(exp_type, universe, product)
                        task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
                    st.text(f"Status: {task.status.value}")

                # SUMMARIZE button
                with col3:
                    task = st.session_state.tasks[summary_key]
                    if st.button("SUMMARIZE", key=f"summary_btn_{summary_key}"):
                        task.status = TaskStatus.IN_PROGRESS
                        my_bar = st.progress(0)
                        for percent_complete in range(100):
                            time.sleep(0.01)
                            my_bar.progress(percent_complete + 1)
                        success = manager.summarize(exp_type, universe, product)
                        task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
                    st.text(f"Status: {task.status.value}")

                st.markdown("---")

if __name__ == "__main__":
    create_experiment_ui()
