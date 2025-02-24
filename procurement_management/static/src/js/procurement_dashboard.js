/** @odoo-module */
import { registry } from "@web/core/registry";
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { ChartRenderer } from "../js/chart_renderer";

export class ProcurementDashboard extends Component {
    static template = "procurement_management.ProcurementDashboard";
    static components = { ChartRenderer };
    static props = {
        action: { type: Object, optional: true },
        actionId: { type: Number, optional: true },
        className: { type: String, optional: true },
    };

    setup() {
        this.orm = useService("orm"); // Odoo ORM service
        this.state = useState({
            selectedSupplier: "",
            suppliers: [],
            approvedRFQs: [],
            selectedDateRange: "",
            productBreakdown: [],
            totalRFQAmount: 0,
            totalRFQs: 0,
            rfqChartData: null,
            productChartData: null,
            rfqTrendsChartData: null,  // 📊 Supplier Performance Chart
            rfqApprovalRateChart: null,  // 📊 RFQ Approval Rate
            productCategoryChart: null,
        });

        this.fetchSuppliers();
    }

    async fetchSuppliers() {
        try {
            const supplierRecords = await this.orm.searchRead(
                "res.partner",
                [["supplier_rank", ">", 0]], // ✅ Fetch only vendors
                ["id", "name"]
            );

            this.state.suppliers = supplierRecords.map(supplier => ({
                id: supplier.id,
                name: supplier.name,
            }));

            console.log("✅ Suppliers Fetched:", this.state.suppliers);
        } catch (error) {
            console.error("❌ Error fetching suppliers:", error);
        }
    }

    selectSupplier(event) {
        this.state.selectedSupplier = event.target.value;
        console.log("✅ Supplier Selected:", this.state.selectedSupplier);
        this.fetchApprovedRFQs();
    }

    selectDateRange(range) {
        this.state.selectedDateRange = range;
        console.log("✅ Date Range Selected:", range);
        this.fetchApprovedRFQs();
    }

    async fetchApprovedRFQs() {
        if (!this.state.selectedSupplier) {
            console.log("⚠️ No supplier selected.");
            return;
        }

        let startDate, endDate;
        const today = new Date();

        switch (this.state.selectedDateRange) {
            case "this_week":
                startDate = new Date(today.setDate(today.getDate() - today.getDay()));
                endDate = new Date(today.setDate(today.getDate() + 6));
                break;
            case "last_week":
                startDate = new Date(today.setDate(today.getDate() - today.getDay() - 7));
                endDate = new Date(today.setDate(today.getDate() + 6));
                break;
            case "last_month":
                startDate = new Date(today.getFullYear(), today.getMonth() - 1, 1);
                endDate = new Date(today.getFullYear(), today.getMonth(), 0);
                break;
            case "last_year":
                startDate = new Date(today.getFullYear() - 1, 0, 1);
                endDate = new Date(today.getFullYear() - 1, 11, 31);
                break;
            default:
                console.log("⚠️ No date range selected.");
                return;
        }

        startDate = startDate.toISOString().split("T")[0];
        endDate = endDate.toISOString().split("T")[0];

        console.log(`🔍 Fetching Approved RFQs for Supplier ID: ${this.state.selectedSupplier}, Date Range: ${startDate} to ${endDate}`);

        try {
            const rfqRecords = await this.orm.searchRead(
                "procurement_management.rfp",
                [
                    ["approved_supplier_id.id", "=", this.state.selectedSupplier],
                    ["status", "=", "accepted"],
                    ["create_date", ">=", startDate],
                    ["create_date", "<=", endDate],
                ],
                ["id", "name", "total_amount", "create_date", "approved_supplier_id", "status"]
            );

            this.state.approvedRFQs = rfqRecords;
            this.fetchProductBreakdown();

            this.state.totalRFQs = rfqRecords.length;
            this.state.totalRFQAmount = rfqRecords.reduce((sum, rfq) => sum + rfq.total_amount, 0);

            if (rfqRecords.length === 0) {
                console.log("❌ No Approved RFQs found for this supplier in the selected date range.");
            } else {
                console.log("✅ Approved RFQs Fetched:", rfqRecords);
                console.log(`✅ Total Approved RFQs: ${this.state.totalRFQs}`);
                console.log(`✅ Total RFQ Amount: $${this.state.totalRFQAmount}`);
            }

            if (rfqRecords.length === 0) {
                console.warn("⚠️ No Approved RFQs found.");
                this.state.supplierContributionChartData = null;
                this.state.monthlyRFQChartData = null;
                return;
            }

            console.log("📦 Raw RFQ Records for Supplier Contribution:", rfqRecords);


            // ✅ **Supplier Contribution Breakdown (Pie Chart)**
            const supplierCounts = {};
            rfqRecords.forEach(rfq => {
                if (rfq.approved_supplier_id && rfq.approved_supplier_id.length > 1) {
                    const supplierName = rfq.approved_supplier_id[1];  // ✅ Extract Supplier Name
                    supplierCounts[supplierName] = (supplierCounts[supplierName] || 0) + rfq.total_amount;  // ✅ Sum RFQ amounts
                }
            });

            console.log("📊 Processed Supplier Contribution Data:", supplierCounts);

            this.state.supplierContributionChartData = {
                labels: Object.keys(supplierCounts),  // ✅ Supplier Names
                datasets: [
                    {
                        label: "Total RFQ Value",
                        data: Object.values(supplierCounts),  // ✅ Supplier RFQ Totals
                        backgroundColor: ["#ff5722", "#03a9f4", "#4caf50", "#ffc107"],
                    }
                ]
            };

            // ✅ Debugging Log
            console.log("✅ Final Supplier Contribution Chart Data:", this.state.supplierContributionChartData);

            // ✅ **Monthly RFQ Trends (Line Chart)**
            const monthCounts = new Array(12).fill(0);
            rfqRecords.forEach(rfq => {
                const monthIndex = new Date(rfq.create_date).getMonth();
                monthCounts[monthIndex]++;
            });

            this.state.monthlyRFQChartData = {
                labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                datasets: [
                    {
                        label: "Total RFQs",
                        data: monthCounts,
                        borderColor: "blue",
                        backgroundColor: "rgba(0,0,255,0.3)",
                        fill: true
                    }
                ]
            };

            console.log("✅ Monthly RFQ Trends Chart Data:", this.state.monthlyRFQChartData);

            let purchaseCount = 0;
            let cancelCount = 0;

            // ✅ Fetch all Purchase Orders for the selected supplier
            const purchaseOrders = await this.orm.searchRead(
                "purchase.order",
                [["partner_id", "=", parseInt(this.state.selectedSupplier)]],
                ["state", "name"]
            );

            console.log("📜 Raw Purchase Orders:", purchaseOrders);

            // ✅ Count RFQs that are 'Purchased' or 'Cancelled'
            purchaseOrders.forEach(order => {
                if (order.state === "purchase") {
                    purchaseCount++;  // Count RFQs that became POs
                } else if (order.state === "cancel") {
                    cancelCount++;  // Count RFQs that were Cancelled
                }
            });

            // ✅ Debugging Log
            console.log(`✅ Final Count → Purchase: ${purchaseCount}, ❌ Cancelled: ${cancelCount}`);

            this.state.rfqApprovalChartData = {
                labels: ["Accepted RFQs", "Rejected RFQs"],
                datasets: [
                    {
                        data: [purchaseCount, cancelCount],
                        backgroundColor: ["green", "red"],
                    }
                ]
            };


            const weeklyCounts = {};

            rfqRecords.forEach(rfq => {
                const week = new Date(rfq.create_date).toLocaleDateString("en-US", { week: "long" });
                weeklyCounts[week] = (weeklyCounts[week] || 0) + 1;
            });

            this.state.rfqWeeklyTrendsChartData = {
                labels: Object.keys(weeklyCounts),
                datasets: [
                    {
                        label: "Total RFQs Per Week",
                        data: Object.values(weeklyCounts),
                        backgroundColor: "#03a9f4",
                    }
                ]
            };

            // ✅ Debugging Log
            console.log("✅ Weekly RFQ Trends Chart Data:", this.state.rfqWeeklyTrendsChartData);

            let totalResponseTime = 0;
            let totalRFQs = 0;

            rfqRecords.forEach(rfq => {
                if (rfq.create_date && rfq.status !== "draft") {
                    const createdDate = new Date(rfq.create_date);
                    const today = new Date();
                    const diffInDays = Math.floor((today - createdDate) / (1000 * 60 * 60 * 24));
                    totalResponseTime += diffInDays;
                    totalRFQs++;
                }
            });

            const avgResponseTime = totalRFQs > 0 ? (totalResponseTime / totalRFQs).toFixed(1) : 0;

            this.state.rfqResponseTimeChartData = {
                labels: ["Average Response Time (Days)"],
                datasets: [
                    {
                        data: [avgResponseTime],
                        backgroundColor: ["#4caf50"],
                    }
                ],
                options: {  // ✅ Include options INSIDE chartData
                    indexAxis: 'y',
                    scales: {
                        x: { suggestedMin: 0, suggestedMax: 10 }
                    }
                }
            };

            // ✅ Debugging Log
            console.log("✅ RFQ Response Time Chart Data:", this.state.rfqResponseTimeChartData);

            const monthlySupplierData = {};
            rfqRecords.forEach(rfq => {
                if (rfq.approved_supplier_id) {
                    const month = new Date(rfq.create_date).toLocaleDateString("en-US", { month: "short" });
                    const supplierName = rfq.approved_supplier_id[1];

                    if (!monthlySupplierData[month]) {
                        monthlySupplierData[month] = {};
                    }

                    monthlySupplierData[month][supplierName] = (monthlySupplierData[month][supplierName] || 0) + rfq.total_amount;
                }
            });

            const months = Object.keys(monthlySupplierData);
            const suppliers = [...new Set(rfqRecords.map(rfq => rfq.approved_supplier_id ? rfq.approved_supplier_id[1] : null))];

            const datasets = suppliers.map(supplier => ({
                label: supplier,
                data: months.map(month => monthlySupplierData[month][supplier] || 0),
                backgroundColor: "#" + Math.floor(Math.random() * 16777215).toString(16), // Random color
            }));

            this.state.monthlySupplierPerformanceChartData = {
                labels: months,
                datasets: datasets
            };

            this.state.monthlySupplierPerformanceChartOptions = {
                scales: {
                    x: { stacked: true },
                    y: { stacked: true }
                }
            };

            // ✅ Debugging Log
            console.log("✅ Monthly Supplier Performance Chart Data:", this.state.monthlySupplierPerformanceChartData);

        } catch (error) {
            console.error("❌ Error fetching Approved RFQs:", error);
        }
    }

    async fetchProductBreakdown() {
        if (!this.state.selectedSupplier) {
            console.log("⚠️ No supplier selected.");
            return;
        }

        try {
            console.log("🔍 Fetching RFP Products for Supplier ID:", this.state.selectedSupplier);

            // 🔹 Fetch RFP Products
            const rfpProducts = await this.orm.searchRead(
                "procurement_management.rfp.product",
                [
                    ["rfp_id", "!=", false],  // ✅ Ensure the RFP reference exists
                    ["rfp_id.approved_supplier_id", "=", parseInt(this.state.selectedSupplier)],  // ✅ Match the selected supplier
                ],
                ["id", "rfp_id", "product_id", "quantity"] // ✅ Fetch only relevant fields
            );

            console.log("📦 RFP Products:", rfpProducts);

            if (rfpProducts.length === 0) {
                console.warn("⚠️ No products found in database matching the supplier and RFQs.");
                this.state.productBreakdown = [];
                return;
            }

            // 🔹 Extract product IDs from fetched RFP products
            const productIds = rfpProducts.map(product => product.product_id[0]);

            // 🔹 Fetch Matching Purchase Order Lines (to get pricing details)
            console.log("🔍 Fetching Purchase Order Lines for Products:", productIds);

            const purchaseLines = await this.orm.searchRead(
                "purchase.order.line",
                [["product_id", "in", productIds], ["order_id.partner_id", "=", parseInt(this.state.selectedSupplier)]],
                ["product_id", "price_unit", "delivery_charge", "price_subtotal", "currency_id"]
            );

            console.log("💰 Purchase Order Lines:", purchaseLines);

            // 🔹 Create a lookup table for unit price & charges from Purchase Order Lines
            const priceLookup = {};
            purchaseLines.forEach(line => {
                priceLookup[line.product_id[0]] = {
                    unitPrice: line.price_unit || 0,
                    deliveryCharge: line.delivery_charge || 0,
                    subtotalPrice: line.price_subtotal || 0,
                    currency: line.currency_id ? line.currency_id[1] : "USD",
                };
            });

            // 🔹 Merge RFP product data with corresponding Purchase Order price details
            this.state.productBreakdown = rfpProducts.map(product => {
                const pricing = priceLookup[product.product_id[0]] || {};  // Get pricing data, fallback to empty object

                return {
                    rfpNumber: product.rfp_id ? product.rfp_id[1] : "N/A",  // ✅ Get RFP Reference Name
                    product: product.product_id ? product.product_id[1] : "Unknown",
                    quantity: product.quantity || 0,
                    unitPrice: pricing.unitPrice !== undefined ? pricing.unitPrice.toFixed(2) : "0.00",
                    deliveryCharge: pricing.deliveryCharge !== undefined ? pricing.deliveryCharge.toFixed(2) : "0.00",
                    subtotalPrice: pricing.subtotalPrice !== undefined ? pricing.subtotalPrice.toFixed(2) : "0.00",
                    currency: pricing.currency || "USD",
                };
            });

            console.log("✅ Final Processed Product Breakdown:", this.state.productBreakdown);

            const productCounts = {};
            this.state.productBreakdown.forEach(product => {
                productCounts[product.product] = (productCounts[product.product] || 0) + product.quantity;
            });

            // ✅ Sort and take the top 5 products
            const sortedProducts = Object.entries(productCounts)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 5);

            this.state.topProductsChartData = {
                labels: sortedProducts.map(p => p[0]),  // ✅ Product Names
                datasets: [
                    {
                        label: "Quantity Ordered",
                        data: sortedProducts.map(p => p[1]),
                        backgroundColor: "#ff9800",
                    }
                ]
            };

            // ✅ Debugging Log
            console.log("✅ Top 5 Products Chart Data:", this.state.topProductsChartData);


        } catch (error) {
            console.error("❌ Error fetching Product Breakdown:", error);
        }
    }


    /** ✅ Supplier Contribution Breakdown (Pie Chart) */
    async fetchSupplierContribution() {
        console.log("🔍 Fetching Supplier Contribution Breakdown...");
        try {
            const supplierRFQData = await this.orm.searchRead(
                "procurement_management.rfp",
                [["status", "=", "accepted"]],
                ["approved_supplier_id"]
            );

            console.log("📦 Raw Supplier RFQ Data:", supplierRFQData);

            if (!supplierRFQData || supplierRFQData.length === 0) {
                console.warn("⚠️ No supplier data found.");
                this.state.supplierContributionChartData = null;
                return;
            }

            // 🔹 Count RFQs per supplier
            const supplierCounts = {};
            supplierRFQData.forEach(rfq => {
                if (rfq.approved_supplier_id) {
                    const supplierName = rfq.approved_supplier_id[1];
                    supplierCounts[supplierName] = (supplierCounts[supplierName] || 0) + 1;
                }
            });

            console.log("📊 Processed Supplier Counts:", supplierCounts);

            // 🔹 Prepare the chart data
            this.state.supplierContributionChartData = {
                labels: Object.keys(supplierCounts),
                datasets: [
                    {
                        label: "Supplier Contribution",
                        data: Object.values(supplierCounts),
                        backgroundColor: ["#ff5722", "#03a9f4", "#4caf50", "#ffc107"]
                    }
                ]
            };

            console.log("✅ Supplier Contribution Chart Data (Final):", JSON.stringify(this.state.supplierContributionChartData, null, 2));

        } catch (error) {
            console.error("❌ Error fetching Supplier Contribution:", error);
        }
    }





    async fetchRFQTrends() {
        console.log("🔍 Fetching Monthly RFQ Trends...");
        try {
            const rfqData = await this.orm.searchRead(
                "procurement_management.rfp",
                [["status", "=", "accepted"]],
                ["create_date"]
            );

            console.log("📦 Raw RFQ Data:", rfqData); // 🔍 Debug log

            if (!rfqData || rfqData.length === 0) {
                console.warn("⚠️ No RFQ data found.");
                this.state.monthlyRFQChartData = null;
                return;
            }

            // 🔹 Count RFQs per month
            const monthCounts = new Array(12).fill(0);
            rfqData.forEach(rfq => {
                const monthIndex = new Date(rfq.create_date).getMonth();
                monthCounts[monthIndex]++;
            });

            console.log("📊 Processed Monthly RFQ Counts:", monthCounts); // 🔍 Debug log

            // 🔹 Prepare chart data
            this.state.monthlyRFQChartData = {
                labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                datasets: [
                    {
                        label: "Total RFQs",
                        data: monthCounts,
                        borderColor: "blue",
                        backgroundColor: "rgba(0,0,255,0.3)",
                        fill: true
                    }
                ]
            };

            console.log("✅ Monthly RFQ Trends Chart Data (Final):", JSON.stringify(this.state.monthlyRFQChartData, null, 2));

        } catch (error) {
            console.error("❌ Error fetching Monthly RFQ Trends:", error);
        }
    }


}

registry.category("actions").add("procurement_management.procurement_dashboard", ProcurementDashboard);