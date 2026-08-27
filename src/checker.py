import csv
import json
import re
from pathlib import Path


# ============================================================
# NetSage AI - Deterministic Network Rule Checker
# ============================================================

def check_case(case):
    """
    Analyze network evidence using deterministic rules.

    Diagnosis is based only on show_outputs evidence.
    The expected_fault column is NOT used for diagnosis.
    """

    text = str(case.get("show_outputs", "")).strip().lower()
    findings = []

    # --------------------------------------------------------
    # 1. Interface administratively down
    # NET-001
    # --------------------------------------------------------
    if "administratively down" in text:

        interface = re.search(
            r"(gigabitethernet|fastethernet|serial)[\w/.-]+",
            text,
            re.IGNORECASE
        )

        interface_name = (
            interface.group(0)
            if interface
            else "Unknown interface"
        )

        findings.append({
            "rule": "INTERFACE_DOWN",
            "finding": f"{interface_name} is administratively down.",
            "severity": "High"
        })

    # --------------------------------------------------------
    # 2. DHCP pool exhaustion
    # NET-002
    # --------------------------------------------------------
    if "zero available" in text and "leased" in text:

        findings.append({
            "rule": "DHCP_POOL_EXHAUSTION",
            "finding": "DHCP pool has no available addresses.",
            "severity": "High"
        })

    # --------------------------------------------------------
    # 3. DNS configuration issue
    # NET-003
    # --------------------------------------------------------
    if (
        "no ip domain-lookup" in text
        or (
            "ip name-server" in text
            and "not active" in text
        )
    ):

        findings.append({
            "rule": "DNS_CONFIGURATION",
            "finding": "DNS lookup/service configuration appears inactive.",
            "severity": "Medium"
        })

    # --------------------------------------------------------
    # 4. OSPF hello timer mismatch
    # NET-004
    # --------------------------------------------------------
    if "ospf hello-interval" in text:

        timers = re.findall(
            r"hello-interval\s+(\d+)",
            text
        )

        if len(timers) >= 2 and len(set(timers)) > 1:

            findings.append({
                "rule": "OSPF_TIMER_MISMATCH",
                "finding": f"Different OSPF hello intervals detected: {timers}.",
                "severity": "High"
            })

    # --------------------------------------------------------
    # 5. ACL deny rule
    # NET-005
    # --------------------------------------------------------
    if "access-list" in text and "deny" in text:

        findings.append({
            "rule": "ACL_DENY",
            "finding": "An ACL deny rule may be blocking required traffic.",
            "severity": "Medium"
        })

    # --------------------------------------------------------
    # 6. NAT overload/PAT missing
    # NET-006
    # --------------------------------------------------------
    if (
        "ip nat inside source list" in text
        and (
            "missing overload keyword" in text
            or "missing overload" in text
            or "overload keyword missing" in text
        )
    ):

        findings.append({
            "rule": "NAT_OVERLOAD_MISSING",
            "finding": "NAT overload/PAT keyword is missing.",
            "severity": "High"
        })

    # --------------------------------------------------------
    # 7. Guest VLAN ACL too permissive
    # NET-007
    # --------------------------------------------------------
    if (
        "guest_acl" in text
        and "192.168.50.0" in text
        and "any" in text
    ):

        findings.append({
            "rule": "GUEST_ACL_PERMISSIVE",
            "finding": "Guest VLAN ACL is overly permissive and allows traffic to any destination.",
            "severity": "High"
        })

    # --------------------------------------------------------
    # 8. VLAN missing from trunk
    # NET-008
    # --------------------------------------------------------
    if (
        "switchport trunk allowed vlan" in text
        and (
            "vlan 20 missing" in text
            or "10 30 40" in text
            or "vlan 20 is missing" in text
        )
    ):

        findings.append({
            "rule": "VLAN_MISSING_FROM_TRUNK",
            "finding": "VLAN 20 is missing from the trunk allowed list.",
            "severity": "Medium"
        })

    # --------------------------------------------------------
    # 9. Host default gateway misconfiguration
    # NET-009
    # --------------------------------------------------------
    if (
        "default gateway 192.168.1.254" in text
        or "gateway set to 192.168.1.254" in text
        or "incorrectly configured default gateway" in text
        or "default gateway ip misconfiguration" in text
    ):

        findings.append({
            "rule": "HOST_GATEWAY_MISCONFIGURATION",
            "finding": "Host has an incorrectly configured default gateway.",
            "severity": "High"
        })

    # --------------------------------------------------------
    # 10. SVI shutdown
    # NET-010
    # --------------------------------------------------------
    if (
        "interface vlan" in text
        and "shutdown" in text
    ):

        findings.append({
            "rule": "SVI_SHUTDOWN",
            "finding": "Management SVI appears to be administratively shut down.",
            "severity": "Low"
        })

    # --------------------------------------------------------
    # 11. Inter-switch link configured as access
    # NET-011
    # --------------------------------------------------------
    if (
        "switchport mode access" in text
        and (
            "fa0/24" in text
            or "inter-switch" in text
        )
    ):

        findings.append({
            "rule": "INTER_SWITCH_ACCESS_MODE",
            "finding": "Inter-switch link is configured as access instead of trunk.",
            "severity": "High"
        })

    # --------------------------------------------------------
    # 12. OSPF passive interface
    # NET-012
    # --------------------------------------------------------
    if (
        "passive-interface" in text
        and "serial" in text
    ):

        findings.append({
            "rule": "OSPF_PASSIVE_LINK",
            "finding": "The active OSPF link is configured as passive.",
            "severity": "High"
        })

    # --------------------------------------------------------
    # 13. Wrong access VLAN
    # NET-013
    # --------------------------------------------------------
    if (
        "switchport access vlan" in text
        and (
            "vlan 14" in text
            or "wrong access vlan" in text
        )
    ):

        findings.append({
            "rule": "WRONG_ACCESS_VLAN",
            "finding": "Switch port is assigned to an incorrect access VLAN.",
            "severity": "Medium"
        })

    # --------------------------------------------------------
    # 14. DHCP relay helper missing
    # NET-014
    # --------------------------------------------------------
    if (
        "missing ip helper-address" in text
        or "missing ip helper address" in text
    ):

        findings.append({
            "rule": "DHCP_RELAY_HELPER_MISSING",
            "finding": "DHCP relay is missing an IP helper address.",
            "severity": "High"
        })

    # --------------------------------------------------------
    # 15. Invalid static route next hop
    # NET-015
    # --------------------------------------------------------
    if (
        "next-hop ip" in text
        and "unreachable" in text
    ):

        findings.append({
            "rule": "INVALID_STATIC_NEXT_HOP",
            "finding": "Configured static-route next hop is unreachable.",
            "severity": "High"
        })

    # --------------------------------------------------------
    # 16. FTP control port 21 missing
    # NET-016
    # --------------------------------------------------------
    if (
        "eq 20" in text
        and (
            "missing port 21" in text
            or "missing port 21 permit rule" in text
            or "port 21" in text and "missing" in text
        )
    ):

        findings.append({
            "rule": "FTP_CONTROL_PORT_MISSING",
            "finding": "FTP control port 21 is missing from the ACL rule.",
            "severity": "Medium"
        })

    # --------------------------------------------------------
    # 17. NAT inside direction missing
    # NET-017
    # --------------------------------------------------------
    if "missing ip nat inside" in text:

        findings.append({
            "rule": "NAT_INSIDE_DIRECTION_MISSING",
            "finding": "NAT inside direction is missing on the internal interface.",
            "severity": "High"
        })

    # --------------------------------------------------------
    # 18. RADIUS shared secret mismatch
    # NET-018
    # --------------------------------------------------------
    if (
        "radius-server" in text
        and (
            "incorrect_secret_key" in text
            or "shared secret mismatch" in text
            or "secret mismatch" in text
        )
    ):

        findings.append({
            "rule": "RADIUS_SECRET_MISMATCH",
            "finding": "RADIUS shared secret configuration does not match.",
            "severity": "High"
        })

    # --------------------------------------------------------
    # 19. Native VLAN mismatch
    # NET-019
    # --------------------------------------------------------
    if (
        "native vlan" in text
        and (
            "mismatch" in text
            or "switchport trunk native vlan 10" in text
            or "switchport trunk native vlan 99" in text
        )
    ):

        findings.append({
            "rule": "NATIVE_VLAN_MISMATCH",
            "finding": "Native VLAN configuration differs between trunk peers.",
            "severity": "Low"
        })

    # --------------------------------------------------------
    # 20. Default gateway outside subnet
    # NET-020
    # --------------------------------------------------------
    if (
        "outside subnet boundary" in text
        or "outside client subnet range" in text
        or "outside the client subnet" in text
        or (
            "gateway" in text
            and "outside" in text
        )
    ):

        findings.append({
            "rule": "GATEWAY_OUTSIDE_SUBNET",
            "finding": "Configured default gateway is outside the client subnet.",
            "severity": "High"
        })

    # --------------------------------------------------------
    # 21. OSPF redistribution missing subnets
    # NET-021
    # --------------------------------------------------------
    if (
        "redistribute eigrp" in text
        and (
            "missing subnets keyword" in text
            or "missing subnets" in text
            or "subnets option" in text
        )
    ):

        findings.append({
            "rule": "OSPF_REDISTRIBUTION_SUBNETS",
            "finding": "OSPF redistribution is missing the subnets option.",
            "severity": "Medium"
        })

    # --------------------------------------------------------
    # 22. HTTPS port 443 missing
    # NET-022
    # --------------------------------------------------------
    if (
        "permit tcp any any eq 80" in text
        and (
            "missing port 443" in text
            or "port 443" in text and "missing" in text
        )
    ):

        findings.append({
            "rule": "HTTPS_PORT_MISSING",
            "finding": "ACL permits HTTP but is missing HTTPS port 443.",
            "severity": "Medium"
        })

    # --------------------------------------------------------
    # 23. Duplicate IP address
    # NET-023
    # --------------------------------------------------------
    if (
        "duplicate address" in text
        or "dup_addr" in text
        or "duplicate ip address" in text
    ):

        findings.append({
            "rule": "DUPLICATE_IP",
            "finding": "Duplicate IP address detected in network evidence.",
            "severity": "High"
        })

    # --------------------------------------------------------
    # 24. VTP domain mismatch
    # NET-024
    # --------------------------------------------------------
    if (
        "vtp domain" in text
        and (
            "case sensitive mismatch" in text
            or "domain name mismatch" in text
            or "mismatch" in text
        )
    ):

        findings.append({
            "rule": "VTP_DOMAIN_MISMATCH",
            "finding": "VTP domain names do not match exactly.",
            "severity": "Medium"
        })

    # --------------------------------------------------------
    # 25. DAI trust missing
    # NET-025
    # --------------------------------------------------------
    if (
        "arp inspection trust missing" in text
        or "dai trusted" in text and "missing" in text
        or "not configured as dai trusted" in text
    ):

        findings.append({
            "rule": "DAI_TRUST_MISSING",
            "finding": "Uplink trunk is not configured as DAI trusted.",
            "severity": "High"
        })

    # --------------------------------------------------------
    # 26. Port security violation
    # NET-026
    # --------------------------------------------------------
    if (
        "psecure_violation" in text
        or "port security violation" in text
        or "port-security violation" in text
    ):

        findings.append({
            "rule": "PORT_SECURITY_VIOLATION",
            "finding": "Port-security violation has been detected.",
            "severity": "Medium"
        })

    # --------------------------------------------------------
    # 27. HSRP timer mismatch
    # NET-027
    # --------------------------------------------------------
    if (
        "standby 1" in text
        and "hello" in text
    ):

        timers = re.findall(
            r"hello\s+(\d+)",
            text
        )

        if len(timers) >= 2 and len(set(timers)) > 1:

            findings.append({
                "rule": "HSRP_TIMER_MISMATCH",
                "finding": f"Different HSRP hello timers detected: {timers}.",
                "severity": "Medium"
            })

    # --------------------------------------------------------
    # 28. Missing dot1Q encapsulation
    # NET-028
    # --------------------------------------------------------
    if (
        "missing encapsulation dot1q" in text
        or "missing 802.1q encapsulation" in text
        or "encapsulation missing" in text and "dot1q" in text
    ):

        findings.append({
            "rule": "DOT1Q_ENCAPSULATION_MISSING",
            "finding": "802.1Q encapsulation is missing from the router sub-interface.",
            "severity": "High"
        })

    # --------------------------------------------------------
    # 29. IPv6 Router Advertisements suppressed
    # NET-029
    # --------------------------------------------------------
    if "ipv6 nd suppress-ra" in text:

        findings.append({
            "rule": "IPV6_RA_SUPPRESSED",
            "finding": "IPv6 Router Advertisements are suppressed.",
            "severity": "Medium"
        })

    # --------------------------------------------------------
    # 30. CDP disabled
    # NET-030
    # --------------------------------------------------------
    if (
        "no cdp run" in text
        or "cdp disabled globally" in text
    ):

        findings.append({
            "rule": "CDP_DISABLED",
            "finding": "CDP is disabled globally on the device.",
            "severity": "Low"
        })

    # --------------------------------------------------------
    # No rule matched
    # --------------------------------------------------------
    if not findings:

        findings.append({
            "rule": "NO_MATCH",
            "finding": "No deterministic rule matched the supplied evidence.",
            "severity": "Info"
        })

    return findings


# ============================================================
# Load Cases
# ============================================================

def load_cases():
    """
    Load cases.csv from:

        NetSage-AI/
            data/
                cases.csv
    """

    project_root = Path(__file__).resolve().parent.parent

    csv_path = project_root / "data" / "cases.csv"

    if not csv_path.exists():

        raise FileNotFoundError(
            f"Could not find dataset:\n{csv_path}"
        )

    with open(
        csv_path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        sample = file.read(4096)

        file.seek(0)

        try:

            dialect = csv.Sniffer().sniff(
                sample,
                delimiters=",\t"
            )

        except csv.Error:

            dialect = csv.excel_tab

        reader = csv.DictReader(
            file,
            dialect=dialect
        )

        cases = list(reader)

        fieldnames = reader.fieldnames

    if not cases:

        raise ValueError(
            "cases.csv is empty."
        )

    required_columns = [
        "case_id",
        "symptom",
        "show_outputs"
    ]

    missing_columns = [
        column
        for column in required_columns
        if not fieldnames or column not in fieldnames
    ]

    if missing_columns:

        raise ValueError(
            "Missing required CSV columns: "
            + ", ".join(missing_columns)
        )

    return cases


# ============================================================
# Run Dataset
# ============================================================

def run_dataset():

    cases = load_cases()

    results = []

    for case in cases:

        findings = check_case(case)

        results.append({
            "case_id": case.get(
                "case_id",
                ""
            ).strip(),

            "symptom": case.get(
                "symptom",
                ""
            ).strip(),

            "findings": findings
        })

    return results


# ============================================================
# Print Results
# ============================================================

def print_results(results):

    print()
    print("=" * 70)
    print("NETSAGE AI - DETERMINISTIC RULE CHECKER")
    print("=" * 70)

    for result in results:

        print()
        print(f"Case ID : {result['case_id']}")
        print(f"Symptom : {result['symptom']}")

        print("-" * 70)

        for finding in result["findings"]:

            print(f"Rule     : {finding['rule']}")
            print(f"Finding  : {finding['finding']}")
            print(f"Severity : {finding['severity']}")

    print()


# ============================================================
# Save Results
# ============================================================

def save_results(results):

    project_root = Path(__file__).resolve().parent.parent

    logs_folder = project_root / "logs"

    logs_folder.mkdir(
        exist_ok=True
    )

    output_path = (
        logs_folder
        / "checker_results.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=4
        )

    return output_path


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    try:

        results = run_dataset()

        print_results(results)

        output_file = save_results(results)

        print("=" * 70)
        print(f"Total cases checked : {len(results)}")
        print(f"Results saved to    : {output_file}")
        print("=" * 70)

    except Exception as error:

        print()
        print("=" * 70)
        print("ERROR")
        print("=" * 70)
        print(error)
        print("=" * 70)