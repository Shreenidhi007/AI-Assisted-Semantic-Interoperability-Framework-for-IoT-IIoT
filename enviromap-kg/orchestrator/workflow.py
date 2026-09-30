"""
Workflow State Machine for the EnviroMap-KG Orchestrator.

Implements the fixed workflow with controlled state transitions,
ensuring agents are invoked in the correct order with no
uncontrolled jumps between stages.
"""

import logging
from typing import Dict, List, Optional, Set

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from models.data_models import WorkflowState


# Valid state transitions
VALID_TRANSITIONS: Dict[WorkflowState, List[WorkflowState]] = {
    WorkflowState.INTAKE: [WorkflowState.DISCOVERY],
    WorkflowState.DISCOVERY: [WorkflowState.REGISTRY_LOOKUP, WorkflowState.ERROR],
    WorkflowState.REGISTRY_LOOKUP: [WorkflowState.KNOWN_CHECK, WorkflowState.ERROR],
    WorkflowState.KNOWN_CHECK: [WorkflowState.RULE_BASED, WorkflowState.ALIGNMENT, WorkflowState.ERROR],
    WorkflowState.RULE_BASED: [WorkflowState.VALIDATION, WorkflowState.ERROR],
    WorkflowState.ALIGNMENT: [WorkflowState.MAPPING, WorkflowState.ERROR],
    WorkflowState.MAPPING: [WorkflowState.REASONING, WorkflowState.ERROR],
    WorkflowState.REASONING: [WorkflowState.VALIDATION, WorkflowState.ERROR],
    WorkflowState.VALIDATION: [WorkflowState.LEARNING, WorkflowState.ERROR],
    WorkflowState.LEARNING: [WorkflowState.TRANSLATION, WorkflowState.COMPLETE, WorkflowState.ERROR],
    WorkflowState.LEARNING: [WorkflowState.REGISTRY_LOOKUP, WorkflowState.TRANSLATION, WorkflowState.COMPLETE, WorkflowState.ERROR],
    WorkflowState.TRANSLATION: [WorkflowState.KG_BUILD, WorkflowState.ERROR],
    WorkflowState.KG_BUILD: [WorkflowState.COMPLETE, WorkflowState.ERROR],
    WorkflowState.COMPLETE: [],  # Terminal state
    WorkflowState.ERROR: [WorkflowState.INTAKE],  # Can retry from start
}


class WorkflowStateMachine:
    """
    Controls the fixed orchestrator workflow.
    
    Prevents uncontrolled jumps between states and tracks
    the complete execution path for audit purposes.
    """

    def __init__(self):
        self.current_state: WorkflowState = WorkflowState.INTAKE
        self.history: List[WorkflowState] = [WorkflowState.INTAKE]
        self.logger = logging.getLogger("enviromap.workflow")
        self._error_count: int = 0
        self._max_errors: int = 3

    def transition(self, target_state: WorkflowState) -> bool:
        """
        Attempt to transition to a new state.
        
        Returns True if the transition is valid and was executed,
        False if the transition is not allowed.
        """
        valid_targets = VALID_TRANSITIONS.get(self.current_state, [])

        if target_state not in valid_targets:
            self.logger.error(
                f"Invalid state transition: {self.current_state.value} -> {target_state.value}. "
                f"Valid targets: {[s.value for s in valid_targets]}"
            )
            return False

        old_state = self.current_state
        self.current_state = target_state
        self.history.append(target_state)

        if target_state == WorkflowState.ERROR:
            self._error_count += 1

        self.logger.info(f"State transition: {old_state.value} -> {target_state.value}")
        return True

    def can_transition_to(self, target_state: WorkflowState) -> bool:
        """Check if a transition to the target state is valid."""
        return target_state in VALID_TRANSITIONS.get(self.current_state, [])

    def reset(self) -> None:
        """Reset the state machine to INTAKE."""
        self.current_state = WorkflowState.INTAKE
        self.history = [WorkflowState.INTAKE]
        self._error_count = 0
        self.logger.info("Workflow state machine reset to INTAKE")

    @property
    def is_complete(self) -> bool:
        """Check if the workflow has reached a terminal state."""
        return self.current_state == WorkflowState.COMPLETE

    @property
    def is_error(self) -> bool:
        """Check if the workflow is in an error state."""
        return self.current_state == WorkflowState.ERROR

    @property
    def should_halt(self) -> bool:
        """Check if too many errors have occurred."""
        return self._error_count >= self._max_errors

    def get_next_states(self) -> List[WorkflowState]:
        """Return the valid next states from the current state."""
        return VALID_TRANSITIONS.get(self.current_state, [])

    def get_execution_path(self) -> List[str]:
        """Return the complete execution path as a list of state names."""
        return [state.value for state in self.history]

    def get_stats(self) -> Dict:
        """Return workflow statistics."""
        return {
            "current_state": self.current_state.value,
            "total_transitions": len(self.history) - 1,
            "error_count": self._error_count,
            "execution_path": self.get_execution_path(),
            "is_complete": self.is_complete,
        }
