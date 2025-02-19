/** @odoo-module */
import { registry } from "@web/core/registry";
import { Component, useRef, onMounted } from "@odoo/owl";


export class ChartRenderer extends Component {
    static template = "procurement_management.ChartRenderer";

    static props = {
        type: { type: String, optional: false },
        title: { type: String, optional: false },
        chartData: { type: Object, optional: false },
        indexAxis: { type: String, optional: true },
    };

    setup() {
        this.chartRef = useRef("chart");
        onMounted(() => this.renderChart());
    }

    async renderChart() {
        console.log("📊 ChartRenderer Processing Data:", JSON.stringify(this.props.chartData, null, 2));

        if (!this.props.chartData || !this.chartRef.el) {
            console.warn("⚠️ No chart data provided OR chartRef.el is null.");
            return;
        }

        if (typeof Chart === "undefined") {
            await this.loadChartJS();
        }

        setTimeout(() => {
            try {
                const ctx = this.chartRef.el.getContext("2d"); // Ensure Canvas context exists
                if (!ctx) {
                    console.error("❌ Chart rendering failed: No valid context found.");
                    return;
                }

                if (this.chart) {
                    this.chart.destroy(); // Destroy existing chart to prevent overlapping
                }

                this.chart = new Chart(ctx, {
                    type: this.props.type || "bar",
                    data: this.props.chartData,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        indexAxis: this.props.indexAxis || "x",
                        plugins: {
                            title: {
                                display: true,
                                text: this.props.title || "Chart",
                            },
                            legend: {
                                position: "bottom",
                            },
                        },
                    },
                });

                console.log("✅ Chart Rendered Successfully!");

            } catch (error) {
                console.error("❌ Error Rendering Chart:", error);
            }
        }, 500);
    }

    async loadChartJS() {
        return new Promise((resolve) => {
            const script = document.createElement("script");
            script.src = "https://cdn.jsdelivr.net/npm/chart.js";
            script.onload = resolve;
            document.head.appendChild(script);
        });
    }
}

ChartRenderer.template = "procurement_management.ChartRenderer";