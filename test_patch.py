sample = """
@dataclass
class CanonicalObservation:
    observation_id: str
    observed_property_uri: str
    observed_property_label: str
    value: Any
    unit: Optional[str] = None
    unit_uri: Optional[str] = None
    result_time: Optional[str] = None
    domain: str = "unknown"
    feature_of_interest: Optional[str] = None
    sensor_uri: Optional[str] = None
    location: Optional[str] = None
    source_table: str = ""
    source_field: str = ""
    source_value: Any = None
    mapping_confidence: float = 0.0
    mapping_method: str = ""
    provenance: Dict[str, Any] = field(default_factory=dict)
"""

target = '    mapping_method: str = ""'
replacement = """    mapping_method: str = ""
    sensor_label: Optional[str] = None
    platform_uri: Optional[str] = None
    platform_label: Optional[str] = None"""

result = sample.replace(target, replacement, 1)
print(result)
assert "sensor_label: Optional[str] = None" in result
print("Assertion passed!")

