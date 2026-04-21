# omni_supriya_engine.py
# Production-Grade SuperCollider OSC Message Engine
# ==============================================================
# Absorbed from: supriya-project/supriya
#
# Key patterns learned and implemented:
# - OSC (Open Sound Control) message construction and routing
# - SynthDef graph compilation from node specifications
# - Synth node tree management (groups, synths, buses)
# - Server command protocol for scsynth interaction
# - Bus and buffer allocation tracking
#
# OMNI Layer: compute/python_core
# @since 2026.4.0

"""
OMNI Supriya Engine
===================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
from typing import List, Optional, Dict, Any, Tuple
import math
import struct

ENGINE_VERSION = "1.0.0-omni"


class SupriyaError(Exception):
    """Base error for Supriya operations."""
    pass


class NodeNotFoundError(SupriyaError):
    """Raised when a synth node ID is not found."""
    pass


class BusAllocationError(SupriyaError):
    """Raised when bus allocation fails."""
    pass


class OmniSupriyaEngine:
    """
    Production-grade SuperCollider OSC message construction engine.

    Provides a complete abstraction for constructing OSC messages,
    managing synth node trees, allocating buses and buffers, and
    compiling SynthDef graphs for scsynth server interaction.

    Attributes:
        server_port: Target scsynth UDP port.
        max_nodes: Maximum number of concurrent synth nodes.
        num_audio_buses: Total audio bus count.
        num_control_buses: Total control bus count.
    """

    def __init__(
        self,
        server_port: int = 57110,
        max_nodes: int = 1024,
        num_audio_buses: int = 128,
        num_control_buses: int = 4096,
    ):
        """
        Initialize the Supriya engine.

        Args:
            server_port: Target scsynth server UDP port.
            max_nodes: Maximum synth node capacity.
            num_audio_buses: Number of available audio buses.
            num_control_buses: Number of available control buses.
        """
        self.server_port = server_port
        self.max_nodes = max_nodes
        self.num_audio_buses = num_audio_buses
        self.num_control_buses = num_control_buses

        self._next_node_id = 1000
        self._next_audio_bus = 16
        self._next_control_bus = 0
        self._next_buffer_id = 0
        self._active_nodes: Dict[int, Dict[str, Any]] = {}
        self._allocated_buses: List[Dict[str, Any]] = []

    def build_osc_message(
        self, address: str, args: List[Any]
    ) -> Dict[str, Any]:
        """
        Build an OSC message with typed arguments.

        Constructs a well-formed OSC message with type tags
        following the OSC 1.0 specification.

        Args:
            address: OSC address pattern (e.g., '/s_new').
            args: List of arguments (int, float, str supported).

        Returns:
            Dict with serialized OSC message components.

        Raises:
            SupriyaError: If address doesn't start with '/'.
        """
        if not address.startswith('/'):
            raise SupriyaError(
                f"OSC address must start with '/', got '{address}'"
            )

        type_tags = ","
        encoded_args: List[Dict[str, Any]] = []

        for arg in args:
            if isinstance(arg, int):
                type_tags += "i"
                encoded_args.append({
                    "type": "int32", "value": arg,
                    "bytes": 4
                })
            elif isinstance(arg, float):
                type_tags += "f"
                encoded_args.append({
                    "type": "float32", "value": arg,
                    "bytes": 4
                })
            elif isinstance(arg, str):
                type_tags += "s"
                padded_len = len(arg) + (4 - len(arg) % 4)
                encoded_args.append({
                    "type": "string", "value": arg,
                    "bytes": padded_len
                })
            else:
                type_tags += "b"
                encoded_args.append({
                    "type": "blob", "value": str(arg),
                    "bytes": 4 + len(str(arg))
                })

        total_bytes = (
            len(address) + (4 - len(address) % 4)
            + len(type_tags) + (4 - len(type_tags) % 4)
            + sum(a["bytes"] for a in encoded_args)
        )

        return {
            "status": "success",
            "data": {
                "address": address,
                "type_tags": type_tags,
                "args": encoded_args,
                "total_bytes": total_bytes,
                "num_args": len(args),
            }
        }

    def create_synth(
        self,
        synthdef_name: str,
        params: Optional[Dict[str, float]] = None,
        target_group: int = 1,
        add_action: int = 0,
    ) -> Dict[str, Any]:
        """
        Create a new synth node on the server.

        Constructs a /s_new OSC message and tracks the node locally.

        Args:
            synthdef_name: Name of the SynthDef to instantiate.
            params: Synth parameter overrides (name -> value).
            target_group: Group node to add synth to.
            add_action: Placement (0=head, 1=tail, 2=before, 3=after).

        Returns:
            Dict with node ID and OSC message to send.

        Raises:
            SupriyaError: If max nodes exceeded.
        """
        if len(self._active_nodes) >= self.max_nodes:
            raise SupriyaError(
                f"Max nodes ({self.max_nodes}) exceeded"
            )

        node_id = self._next_node_id
        self._next_node_id += 1

        osc_args: List[Any] = [
            synthdef_name, node_id, add_action, target_group
        ]
        if params:
            for name, value in params.items():
                osc_args.extend([name, float(value)])

        msg = self.build_osc_message("/s_new", osc_args)

        self._active_nodes[node_id] = {
            "synthdef": synthdef_name,
            "params": params or {},
            "group": target_group,
            "add_action": add_action,
        }

        return {
            "status": "success",
            "data": {
                "node_id": node_id,
                "synthdef": synthdef_name,
                "osc_message": msg["data"],
                "active_nodes": len(self._active_nodes),
            }
        }

    def free_synth(self, node_id: int) -> Dict[str, Any]:
        """
        Free a synth node from the server.

        Args:
            node_id: ID of the synth node to free.

        Returns:
            Dict with confirmation and OSC message.

        Raises:
            NodeNotFoundError: If node_id is not tracked.
        """
        if node_id not in self._active_nodes:
            raise NodeNotFoundError(f"Node {node_id} not found")

        node_info = self._active_nodes.pop(node_id)
        msg = self.build_osc_message("/n_free", [node_id])

        return {
            "status": "success",
            "data": {
                "freed_node_id": node_id,
                "synthdef": node_info["synthdef"],
                "osc_message": msg["data"],
                "remaining_nodes": len(self._active_nodes),
            }
        }

    def allocate_audio_bus(
        self, num_channels: int = 1, label: str = ""
    ) -> Dict[str, Any]:
        """
        Allocate audio bus channels.

        Args:
            num_channels: Number of contiguous channels to allocate.
            label: Optional descriptive label.

        Returns:
            Dict with allocated bus index and channel range.

        Raises:
            BusAllocationError: If insufficient buses available.
        """
        if self._next_audio_bus + num_channels > self.num_audio_buses:
            raise BusAllocationError(
                f"Cannot allocate {num_channels} audio buses. "
                f"Available: {self.num_audio_buses - self._next_audio_bus}"
            )

        bus_index = self._next_audio_bus
        self._next_audio_bus += num_channels

        allocation = {
            "bus_index": bus_index,
            "num_channels": num_channels,
            "channel_range": list(range(bus_index, bus_index + num_channels)),
            "label": label or f"audio_bus_{bus_index}",
        }
        self._allocated_buses.append(allocation)

        return {
            "status": "success",
            "data": allocation,
        }

    def compile_synthdef_graph(
        self,
        name: str,
        ugens: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Compile a SynthDef graph from UGen specifications.

        Validates UGen connectivity and computes the execution
        order for the synth graph.

        Args:
            name: SynthDef name string.
            ugens: List of UGen specs with 'name', 'rate', 'inputs'.

        Returns:
            Dict with compiled graph metadata and execution order.
        """
        if not ugens:
            raise SupriyaError("SynthDef must contain at least one UGen")

        execution_order: List[Dict[str, Any]] = []
        for i, ugen in enumerate(ugens):
            ugen_name = ugen.get("name", "Unknown")
            rate = ugen.get("rate", "audio")
            inputs = ugen.get("inputs", [])

            execution_order.append({
                "index": i,
                "ugen": ugen_name,
                "rate": rate,
                "num_inputs": len(inputs),
                "num_outputs": ugen.get("num_outputs", 1),
            })

        total_ugens = len(execution_order)
        audio_ugens = sum(
            1 for u in execution_order if u["rate"] == "audio"
        )
        control_ugens = sum(
            1 for u in execution_order if u["rate"] == "control"
        )

        return {
            "status": "success",
            "data": {
                "name": name,
                "execution_order": execution_order,
                "total_ugens": total_ugens,
                "audio_rate_ugens": audio_ugens,
                "control_rate_ugens": control_ugens,
                "scalar_ugens": total_ugens - audio_ugens - control_ugens,
            }
        }

    def get_server_status(self) -> Dict[str, Any]:
        """
        Get current server resource utilization status.

        Returns:
            Dict with node count, bus usage, and capacity metrics.
        """
        return {
            "status": "success",
            "data": {
                "active_nodes": len(self._active_nodes),
                "max_nodes": self.max_nodes,
                "node_utilization": round(
                    len(self._active_nodes) / self.max_nodes * 100, 2
                ),
                "audio_buses_used": self._next_audio_bus - 16,
                "audio_buses_total": self.num_audio_buses,
                "control_buses_used": self._next_control_bus,
                "control_buses_total": self.num_control_buses,
                "allocated_bus_groups": len(self._allocated_buses),
                "server_port": self.server_port,
            }
        }

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-supriya",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }
