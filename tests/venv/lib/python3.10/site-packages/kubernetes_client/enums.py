from typing import Iterator, Optional, Union, List, Tuple, Dict
from enum import Enum, unique
import json


__all__ = [
    "ServiceType",
    "ServiceStatus",
    "PodPhase",
    "PodStatus",
    "ContainerState",
    "ContainerStateReason",
    "PodReason",
    "PodConditionType",
    "PodConditionStatus",
    "PodConditionReason",
    "TektonReason",
    "TektonStatus",
    "ActionStatus",
    "JobResult",
]


@unique
class BaseEnum(str, Enum):

    @property
    def describe(self):
        # self is the member here
        return self.name, self.value


    def __str__(self) -> str:
        return str(self.value)


    def __repr__(self) -> str:
        return json.dumps(self.value)


    def __eq__(cls, v):
        return cls.value == cls.of(v).value


    @classmethod
    def _missing_(cls, type):
        if isinstance(type, str):
            for item in cls:
                if item.value.lower() == type.lower():
                    return item
        else:
            for item in cls:
                if item.value == type:
                    return item

    def _missing_(cls, type):
        try:
            if isinstance(type, str):
                matched = [
                    item for item in cls if item.value.lower() == type.lower()
                ]
            else:
                matched = [item for item in cls if item.value == type]
            return matched[0]

        except IndexError:
            raise ValueError(f"'{type}' is not in {cls.__name__}")


    def ignore_case(self) -> str:
        return str(self.value).lower()


    @classmethod
    def of(cls, type):
        return cls._missing_(type)


def use_enum_values(x: Union[Enum, BaseEnum]):
    # (cls._member_map_[name] for name in cls._member_names_)
    return [e.value for e in x]


class ServiceType(BaseEnum):
    LoadBalancer = "LoadBalancer"
    NodePort = "NodePort"
    ClusterIP = "ClusterIP"


class ServiceStatus(BaseEnum):
    """THIS ORDER IS REFERENCED. DO NOT CHANGE IT.
    """
    WAITING = "WAITING"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    COMPLETED = "COMPLETED"
    DELETED = "DELETED"
    UNKNOWN = "UNKNOWN"
    ERROR = "ERROR"


class PodPhase(BaseEnum):
    """
    See: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-phase
    """
    PENDING = "Pending"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    UNKNOWN = "Unknown"


# PodStatus = PodPhase
class PodStatus(BaseEnum):
    """
    See: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-phase
    """
    PENDING = "Pending"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    UNKNOWN = "Unknown"


class ContainerState(BaseEnum):
    """
    See: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#container-states
    """
    WAITING = "Waiting"
    RUNNING = "Running"
    TERMINATED = "Terminated"


class ContainerStateReason(BaseEnum):
    COMPLETED = "Completed"
    CRASHLOOPBACKOFF = "CrashLoopBackOff"
    OOMKILLED = "OOMKilled"
    CONTAINERSNOTREADY = "ContainersNotReady"
    EVICTED = "Evicted"


# PodReason = ContainerStateReason
class PodReason(BaseEnum):
    COMPLETED = "Completed"
    CRASHLOOPBACKOFF = "CrashLoopBackOff"
    OOMKILLED = "OOMKilled"
    CONTAINERSNOTREADY = "ContainersNotReady"
    EVICTED = "Evicted"


class PodConditionType(BaseEnum):
    """
    See: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-conditions
    """
    PODSCHEDULED = "PodScheduled"
    CONTAINERSREADY = "ContainersReady"
    INITIALIZED = "Initialized"
    READY = "Ready"


class PodConditionStatus(BaseEnum):
    """
    See: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-conditions
    """
    TRUE = "True"
    FALSE = "False"
    UNKNOWN = "Unknown"


class PodConditionReason(BaseEnum):
    """
    See: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-conditions
    """
    TRUE = "True"
    FALSE = "False"
    UNKNOWN = "Unknown"


class TektonReason(BaseEnum):
    """THIS ORDER IS REFERENCED. DO NOT CHANGE IT.
    """
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    RUNNING = "Running"


# TektonStatus = PodConditionStatus
class TektonStatus(BaseEnum):
    """
    See: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-conditions
    """
    TRUE = "True"
    FALSE = "False"
    UNKNOWN = "Unknown"


class ActionStatus(BaseEnum):
    ADDED = "ADDED"
    MODIFIED = "MODIFIED"
    DELETED = "DELETED"
    ERROR = "ERROR"


class JobResult(BaseEnum):
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
