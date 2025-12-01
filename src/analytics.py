def generate_report(data):
    report = []
    report.append("=== Business Analytics Dashboard ===")
    report.append(f"Total Packages: {data['total_packages']}")
    report.append(f"Delivered: {data['delivered_packages']}")
    report.append(f"Pending: {data['pending_packages']}")
    if data['total_packages'] > 0:
        success_rate = (data['delivered_packages'] / data['total_packages']) * 100
        report.append(f"Success Rate: {success_rate:.1f}%")
    else:
        report.append("Success Rate: N/A")
    
    report.append(f"Total Fleet Distance: {data['total_distance']:.2f} km")
    report.append(f"Active Trucks: {data['active_trucks']}")
    report.append("====================================")
    return "\n".join(report)
