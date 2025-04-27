# graph_visualizer/views.py

from django.shortcuts import render
import networkx as nx
from pyvis.network import Network
import math
import json
from bs4 import BeautifulSoup
import io # To handle potential string buffer for older pyvis versions

def display_supply_chain_graph(request):
    """
    View to generate and display the interactive, animated supply chain graph.
    """
    print("--- Generating Interactive Animated Pyvis Graph for Django View ---")

    # --- (Steps 1 & 2: Data, Weight Calc, Graph Construction - From Script) ---
    suppliers = ["S1", "S2", "S3"]
    components = ["Battery", "Controller", "Frame"]
    products = ["ScooterA", "ScooterB"]
    supplier_component_data = [
        ("S1", "Battery",    {"unitCost": 15, "reliability": 0.85, "minQty": 100, "orderedQty": 150, "leadTime": 2}),
        ("S1", "Controller", {"unitCost": 22, "reliability": 0.90, "minQty": 50,  "orderedQty": 60,  "leadTime": 3}),
        ("S2", "Battery",    {"unitCost": 12, "reliability": 0.78, "minQty": 200, "orderedQty": 180, "leadTime": 4}),
        ("S2", "Frame",      {"unitCost": 45, "reliability": 0.82, "minQty": 75,  "orderedQty": 80,  "leadTime": 1.5}),
        ("S3", "Controller", {"unitCost": 18, "reliability": 0.95, "minQty": 60,  "orderedQty": 65,  "leadTime": 2.5}),
        ("S3", "Frame",      {"unitCost": 38, "reliability": 0.88, "minQty": 90,  "orderedQty": 100, "leadTime": 2}),
    ]
    component_product_data = [
        ("Battery", "ScooterA"), ("Controller", "ScooterA"),
        ("Battery", "ScooterB"), ("Frame", "ScooterB"),
    ]
    def calculate_python_edge_weight(attrs):
        unitCost=attrs.get("unitCost",0); reliability=max(attrs.get("reliability",0.01),0.001)
        minQty=attrs.get("minQty",1); orderedQty=attrs.get("orderedQty",1)
        leadTime=max(attrs.get("leadTime",1),0.001)
        try: return round((unitCost*(1.0/reliability)*max(minQty,orderedQty))/leadTime,2)
        except Exception: return float('inf')

    node_base_styles_dict = {}
    edge_base_styles_dict = {}
    base_node_styling = {
        'supplier':   {'color': {'background': '#C0C0C0', 'border': '#808080'}, 'size': 15},
        'component':  {'color': {'background': '#ADD8E6', 'border': '#6495ED'}, 'size': 12},
        'product':    {'color': {'background': '#90EE90', 'border': '#3CB371'}, 'size': 20},
    }
    default_node_border_width = 1
    base_edge_styling = {
        'SUPPLIES': {'color': {'color': '#A9A9A9', 'highlight': '#808080'}, 'width': 1, 'dashes': False},
        'USED_IN':  {'color': {'color': '#6495ED', 'highlight': '#00008B'}, 'width': 2, 'dashes': False},
    }
    highlight_node_color={'background':'#FFFF00', 'border': '#FFA500'}; highlight_node_size_factor=1.5
    highlight_bottleneck_color={'background':'#FF6347', 'border': '#DC143C'}; highlight_bottleneck_borderwidth=3
    highlight_edge_optimal={'color':{'color':'#32CD32', 'highlight': '#228B22'},'width':3,'dashes':True};
    highlight_edge_product={'color':{'color':'#FFA500', 'highlight': '#FF8C00'},'width':4,'dashes':False}

    G = nx.DiGraph()
    for node in suppliers:
        G.add_node(node, title=f"Supplier: {node}", level=0, type='supplier')
        style = base_node_styling['supplier'].copy(); style['borderWidth'] = default_node_border_width
        node_base_styles_dict[node] = style
    for node in components:
        G.add_node(node, title=f"Component: {node}", level=1, type='component')
        style = base_node_styling['component'].copy(); style['borderWidth'] = default_node_border_width
        node_base_styles_dict[node] = style
    for node in products:
        G.add_node(node, title=f"Product: {node}", level=2, type='product')
        style = base_node_styling['product'].copy(); style['borderWidth'] = default_node_border_width
        node_base_styles_dict[node] = style
    for u, v, attrs in supplier_component_data:
        weight = calculate_python_edge_weight(attrs); edge_id = f"{u}_to_{v}"
        G.add_edge(u, v, id=edge_id, weight=weight, title=f'Cost Factor: {weight:.2f}', type='SUPPLIES')
        edge_base_styles_dict[edge_id] = base_edge_styling['SUPPLIES'].copy()
    for u, v in component_product_data:
        edge_id = f"{u}_to_{v}"
        G.add_edge(u, v, id=edge_id, weight=0, title='Used In', type='USED_IN')
        edge_base_styles_dict[edge_id] = base_edge_styling['USED_IN'].copy()

    print(f"Django View: NetworkX Graph Created. Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")

    # --- (Step 3: Calculate Path Info - From Script) ---
    print("Django View: Calculating path information...")
    all_path_data = {}
    def find_optimal_paths_and_bottlenecks(graph, product_id):
        if product_id not in graph: return [], [], []
        req_comp = [n for n in graph.predecessors(product_id) if graph.nodes[n]['type'] == 'component']
        if not req_comp:
            prod_edges = [d.get('id',f"{u}_to_{v}") for u,v,d in graph.in_edges(product_id, data=True)]
            return [], [], prod_edges
        optimal_edges = []; bottleneck_nodes = []
        for comp in req_comp:
            sup_edges_data = [(u, v, d) for u, v, d in graph.in_edges(comp, data=True) if graph.nodes[u]['type'] == 'supplier']
            if not sup_edges_data: continue
            min_weight_edge = min(sup_edges_data, key=lambda e: e[2].get('weight', float('inf')))
            min_weight_edge_id = min_weight_edge[2].get('id', f"{min_weight_edge[0]}_to_{min_weight_edge[1]}")
            optimal_edges.append(min_weight_edge_id)
            if len(sup_edges_data) == 1: bottleneck_nodes.append(comp)
        product_edges = [d.get('id',f"{u}_to_{v}") for u,v,d in graph.in_edges(product_id, data=True)]
        return optimal_edges, bottleneck_nodes, product_edges

    def get_path_nodes(graph, product_id, product_edge_ids, optimal_edge_ids):
        nodes_in_path = set([product_id])
        for edge_id in product_edge_ids:
            edge_data = next(((u,v) for u, v, data in graph.edges(data=True) if data.get('id') == edge_id), None)
            if edge_data: nodes_in_path.add(edge_data[0])
        for edge_id in optimal_edge_ids:
            edge_data = next(((u,v) for u, v, data in graph.edges(data=True) if data.get('id') == edge_id), None)
            if edge_data: nodes_in_path.add(edge_data[0]); nodes_in_path.add(edge_data[1])
        req_comp = [n for n in graph.predecessors(product_id) if graph.nodes[n]['type'] == 'component']
        for comp in req_comp: nodes_in_path.add(comp)
        return list(nodes_in_path)

    for product_id in products:
        opt_edge_ids, bottle_nodes, prod_edge_ids = find_optimal_paths_and_bottlenecks(G, product_id)
        path_nodes = get_path_nodes(G, product_id, prod_edge_ids, opt_edge_ids)
        all_path_data[product_id] = {"nodes": path_nodes, "optimal_edges": opt_edge_ids, "product_edges": prod_edge_ids, "bottlenecks": bottle_nodes}

    path_data_json = json.dumps(all_path_data)
    node_styles_json = json.dumps(node_base_styles_dict)
    edge_styles_json = json.dumps(edge_base_styles_dict)
    print("Django View: Path data prepared for JavaScript.")

    # --- (Step 4: Generate Base Pyvis HTML String - MODIFIED FOR DJANGO) ---
    print("Django View: Generating base Pyvis HTML string...")
    net = Network(notebook=False, height='90vh', width='100%', directed=True, bgcolor='#FFFFFF', font_color='black')
    net.from_nx(G)
    net.set_options("""
    {
      "nodes": {"font": {"size": 10, "face": "arial"}},
      "edges": {
        "smooth": {"enabled": true, "type": "cubicBezier", "forceDirection": "horizontal", "roundness": 0.5},
        "font": {"size": 8, "align": "middle"},
        "arrows": {"to": { "enabled": true, "scaleFactor": 0.5 }}
      },
      "layout": {"hierarchical": {"enabled": true, "direction": "LR", "sortMethod": "directed", "levelSeparation": 300, "nodeSpacing": 150}},
      "physics": {"enabled": false},
      "interaction": {"tooltipDelay": 200, "navigationButtons": true, "keyboard": true}
    }
    """)

    # --- Generate HTML string IN MEMORY ---
    base_html_content = "<html><body>Error generating graph HTML.</body></html>" # Default error msg
    try:
         # Try direct string generation (common in recent pyvis)
         base_html_content = net.generate_html()
         print("Django View: Successfully generated HTML string using generate_html().")
    except AttributeError:
         # Fallback for older pyvis: save to a string buffer
         print("Django View: generate_html() not found, attempting save_graph to buffer...")
         from io import BytesIO # Already imported io, but good to have specific import here
         html_buffer = BytesIO() # Use BytesIO as save_graph might write bytes
         try:
            net.save_graph(html_buffer)
            html_buffer.seek(0)
            base_html_content = html_buffer.read().decode('utf-8') # Decode if needed
            print("Django View: Successfully generated HTML string using save_graph() to buffer.")
         except Exception as save_err:
             print(f"Django View: Error during save_graph to buffer: {save_err}")
             # Keep default error message
    except Exception as e:
         print(f"Django View: Error generating base HTML: {e}")
         # Keep default error message

    # --- (Step 5: Define JavaScript - Use the Corrected F-String Version) ---
    print("Django View: Defining JavaScript for animation...")
    # *** USE THE CORRECTED JAVASCRIPT F-STRING FROM PREVIOUS STEP ***
    # (Double-check all {{ }}, $\{{ }}, \\d escapes are correct in YOUR editor)
    javascript_code = f"""
<script type="text/javascript">
    // Data passed from Python
    const pathData = {path_data_json};
    const baseNodeStyles = {node_styles_json};
    const baseEdgeStyles = {edge_styles_json};

    // Highlight style definitions
    // Using {{}} for JS object literals
    const highlightNodeStyleDef = {{ color: {json.dumps(highlight_node_color)}, borderWidth: {default_node_border_width} }};
    const highlightBottleneckStyleDef = {{ color: {json.dumps(highlight_bottleneck_color)}, borderWidth: {highlight_bottleneck_borderwidth} }};
    const highlightEdgeOptimalStyleDef = {json.dumps(highlight_edge_optimal)};
    const highlightEdgeProductStyleDef = {json.dumps(highlight_edge_product)};
    const nodeSizeFactor = {highlight_node_size_factor};

    // --- Animation Globals ---
    let currentAnimationId = null;
    let animationStartTime = 0;
    const animationDuration = 400; // milliseconds
    let nodesToAnimate = []; // Array of {{ id, startStyle, targetStyle }}
    let edgesToAnimate = []; // Array of {{ id, startStyle, targetStyle }}

    // --- Helper: Parse Hex Color (#RRGGBB) to {{r, g, b}} ---
    function parseColor(hex) {{ // Start function body {{
        if (!hex || typeof hex !== 'string') return null;
        // Regex needs \\d and {{n}} inside f-string
        let result = /^#?([a-f\\d]{{2}})([a-f\\d]{{2}})([a-f\\d]{{2}})$/i.exec(hex);
        return result ? {{ // JS object literal {{
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        }} : null; // End JS object literal }}
    }} // End function body }}

    // --- Helper: Convert {{r, g, b}} to Hex Color ---
    function formatColor(rgb) {{ // Start function body {{
        if (!rgb) return null;
        const toHex = c => {{ // Start arrow function {{
            const hex = Math.round(c).toString(16);
            return hex.length == 1 ? "0" + hex : hex;
        }}; // End arrow function }}
        // Escaping the template literal placeholders inside the JS string $\{{ ... }}
    return `#${{toHex(rgb.r)}}${{toHex(rgb.g)}}${{toHex(rgb.b)}}`;
    }} // End function body }}

    // --- Helper: Linear Interpolation ---
    function lerp(start, end, progress) {{ // Start function body {{
        return start + (end - start) * progress;
    }} // End function body }}

    // --- Function to Apply Base Styles (Initial Load Only) ---
    function applyBaseStyles() {{ // Start function body {{
        console.log("Applying initial base styles.");
        // Use the structures defined in Python directly
        // Using {{}} for JS object literal in map
        let nodeUpdates = Object.keys(baseNodeStyles).map(id => ({{ id, ...baseNodeStyles[id] }}));
        let edgeUpdates = Object.keys(baseEdgeStyles).map(id => ({{ id, ...baseEdgeStyles[id] }}));

        if (nodeUpdates.length > 0 && network.body?.data?.nodes) {{ // Start if {{
            network.body.data.nodes.update(nodeUpdates);
        }} // End if }}
        if (edgeUpdates.length > 0 && network.body?.data?.edges) {{ // Start if {{
            network.body.data.edges.update(edgeUpdates);
        }} // End if }}
        console.log("Initial base styles applied.");
    }} // End function body }}


    // --- Animation Step Function ---
    function animateStep(timestamp) {{ // Start function body {{
        if (!animationStartTime) animationStartTime = timestamp;
        const elapsed = timestamp - animationStartTime;
        const progress = Math.min(1.0, elapsed / animationDuration);

        let nodeUpdates = [];
        let edgeUpdates = [];

        // Animate Nodes
        nodesToAnimate.forEach(anim => {{ // Start forEach arrow function {{
            const currentStyle = {{}}; // JS object literal {{}}
            const start = anim.startStyle;
            const target = anim.targetStyle;

            // Interpolate Size
            if (start.size !== undefined && target.size !== undefined) {{ // Start if {{
                currentStyle.size = lerp(start.size, target.size, progress);
            }} // End if }}
            // Interpolate Border Width
            if (start.borderWidth !== undefined && target.borderWidth !== undefined) {{ // Start if {{
                currentStyle.borderWidth = lerp(start.borderWidth, target.borderWidth, progress);
            }} // End if }}

            // Interpolate Colors (background and border)
            currentStyle.color = {{}}; // JS object literal {{}}
            const startBg = parseColor(start.color?.background);
            const targetBg = parseColor(target.color?.background);
            if (startBg && targetBg) {{ // Start if {{
                currentStyle.color.background = formatColor({{ // JS object literal {{
                    r: lerp(startBg.r, targetBg.r, progress),
                    g: lerp(startBg.g, targetBg.g, progress),
                    b: lerp(startBg.b, targetBg.b, progress)
                }}); // End JS object literal }}
            }} else {{ currentStyle.color.background = target.color?.background; }} // Fallback // End if }}

            const startBorder = parseColor(start.color?.border);
            const targetBorder = parseColor(target.color?.border);
            if (startBorder && targetBorder) {{ // Start if {{
                currentStyle.color.border = formatColor({{ // JS object literal {{
                    r: lerp(startBorder.r, targetBorder.r, progress),
                    g: lerp(startBorder.g, targetBorder.g, progress),
                    b: lerp(startBorder.b, targetBorder.b, progress)
                }}); // End JS object literal }}
            }} else {{ currentStyle.color.border = target.color?.border; }} // Fallback // End if }}

            nodeUpdates.push({{ id: anim.id, ...currentStyle }}); // JS object literal {{}}
        }}); // End forEach arrow function }}

        // Animate Edges
        edgesToAnimate.forEach(anim => {{ // Start forEach arrow function {{
            const currentStyle = {{}}; // JS object literal {{}}
            const start = anim.startStyle;
            const target = anim.targetStyle;

            // Interpolate Width
            if (start.width !== undefined && target.width !== undefined) {{ // Start if {{
                currentStyle.width = lerp(start.width, target.width, progress);
            }} // End if }}

            // Interpolate Color
            currentStyle.color = {{}}; // JS object literal {{}}
            const startColor = parseColor(start.color?.color);
            const targetColor = parseColor(target.color?.color);
             if (startColor && targetColor) {{ // Start if {{
                 currentStyle.color.color = formatColor({{ // JS object literal {{
                     r: lerp(startColor.r, targetColor.r, progress),
                     g: lerp(startColor.g, targetColor.g, progress),
                     b: lerp(startColor.b, targetColor.b, progress)
                 }}); // End JS object literal }}
             }} else {{ currentStyle.color.color = target.color?.color; }} // Fallback // End if }}

            // Dashes: Apply target style only at the end
             currentStyle.dashes = (progress < 1.0 && start.dashes !== undefined) ? start.dashes : target.dashes;
             // Keep highlight color consistent during animation
             currentStyle.color.highlight = start.color?.highlight;

            edgeUpdates.push({{ id: anim.id, ...currentStyle }}); // JS object literal {{}}
        }}); // End forEach arrow function }}


        // Apply Updates
        if (nodeUpdates.length > 0 && network.body?.data?.nodes) {{ // Start if {{
            network.body.data.nodes.update(nodeUpdates);
        }} // End if }}
         if (edgeUpdates.length > 0 && network.body?.data?.edges) {{ // Start if {{
             network.body.data.edges.update(edgeUpdates);
         }} // End if }}

        // Continue or Stop
        if (progress < 1.0) {{ // Start if {{
            currentAnimationId = requestAnimationFrame(animateStep);
        }} else {{ // Start else {{
            console.log("Animation finished.");
            currentAnimationId = null;
            // Ensure final 'dashes' state is set correctly (sometimes update misses last frame)
            let finalEdgeUpdates = edgesToAnimate
                .filter(anim => anim.startStyle.dashes !== anim.targetStyle.dashes)
                .map(anim => ({{id: anim.id, dashes: anim.targetStyle.dashes}})); // JS object literal {{}}
            if (finalEdgeUpdates.length > 0 && network.body?.data?.edges) {{ // Added check {{
                 network.body.data.edges.update(finalEdgeUpdates);
            }} // End added check }}
        }} // End if/else }}
    }} // End function body }}

    // --- Function to Start an Animation ---
    function startAnimation(targetNodeStylesMap, targetEdgeStylesMap) {{ // Start function body {{
        console.log("Preparing animation...");
        // Cancel any ongoing animation
        if (currentAnimationId !== null) {{ // Start if {{
            cancelAnimationFrame(currentAnimationId);
            currentAnimationId = null;
            console.log("Cancelled previous animation.");
        }} // End if }}

        nodesToAnimate = [];
        edgesToAnimate = [];

        // Check if network data is ready
        if (!network || !network.body || !network.body.data || !network.body.data.nodes || !network.body.data.edges) {{ // Start if {{
            console.error("Network data not fully initialized. Cannot start animation.");
            return;
        }} // End if }}

        const allNodeIds = network.body.data.nodes.getIds();
        const allEdgeIds = network.body.data.edges.getIds();

        // Prepare node animations
        allNodeIds.forEach(id => {{ // Start forEach arrow function {{
            const currentNodeData = network.body.data.nodes.get(id);
            // Use JS template literal escaping $\{{id}}
            if (!currentNodeData) {{ console.warn(`Node data for ${{id}} not found`); return; }} // Added check
             // Deep copy needed for nested color object
            const startStyle = JSON.parse(JSON.stringify({{ // JS object literal {{}}
                size: currentNodeData.size,
                borderWidth: currentNodeData.borderWidth,
                color: currentNodeData.color || {{}} // Ensure color object exists {{}}
            }})); // End object literal }}
            // Target is either the specific highlight or the base style
            const targetStyle = targetNodeStylesMap[id] || baseNodeStyles[id];

             // Only animate if styles are different or target exists
            if (targetStyle) {{ // Start if {{ check later
                 // Ensure targetStyle has needed props, copying from base if missing in highlight def
                 const finalTarget = JSON.parse(JSON.stringify(targetStyle)); // Deep copy
                 if (!finalTarget.color) finalTarget.color = {{}}; // JS object literal {{}}
                 if (!finalTarget.color.background) finalTarget.color.background = baseNodeStyles[id]?.color?.background;
                 if (!finalTarget.color.border) finalTarget.color.border = baseNodeStyles[id]?.color?.border;
                 if (finalTarget.size === undefined) finalTarget.size = baseNodeStyles[id]?.size;
                 if (finalTarget.borderWidth === undefined) finalTarget.borderWidth = baseNodeStyles[id]?.borderWidth;

                // Only add if START and TARGET styles are actually different after finalisation
                 if (JSON.stringify(startStyle) !== JSON.stringify(finalTarget)) {{ // Start if {{
                    nodesToAnimate.push({{ id, startStyle, targetStyle: finalTarget }}); // JS object literal {{}}
                 }} // End if }}
            }} // End if }}
        }}); // End forEach arrow function }}

        // Prepare edge animations
        allEdgeIds.forEach(id => {{ // Start forEach arrow function {{
            const currentEdgeData = network.body.data.edges.get(id);
            // Use JS template literal escaping $\{{id}}
             if (!currentEdgeData) {{ console.warn(`Edge data for ${{id}} not found`); return; }} // Added check
            const startStyle = JSON.parse(JSON.stringify({{ // JS object literal {{}}
                width: currentEdgeData.width,
                dashes: currentEdgeData.dashes,
                color: currentEdgeData.color || {{}} // JS object literal {{}}
            }})); // End object literal }}
            const targetStyle = targetEdgeStylesMap[id] || baseEdgeStyles[id];

            if (targetStyle) {{ // Start if {{ check later
                 const finalTarget = JSON.parse(JSON.stringify(targetStyle)); // Deep copy
                 if (!finalTarget.color) finalTarget.color = {{}}; // JS object literal {{}}
                 if (!finalTarget.color.color) finalTarget.color.color = baseEdgeStyles[id]?.color?.color;
                 if (finalTarget.width === undefined) finalTarget.width = baseEdgeStyles[id]?.width;
                 if (finalTarget.dashes === undefined) finalTarget.dashes = baseEdgeStyles[id]?.dashes;

                 // Only add if START and TARGET styles are actually different
                 if (JSON.stringify(startStyle) !== JSON.stringify(finalTarget)) {{ // Start if {{
                    edgesToAnimate.push({{ id, startStyle, targetStyle: finalTarget }}); // JS object literal {{}}
                 }} // End if }}
             }} // End if }}
        }}); // End forEach arrow function }}


        if (nodesToAnimate.length === 0 && edgesToAnimate.length === 0) {{ // Start if {{
            console.log("No style changes detected, animation skipped.");
            return;
        }} // End if }}

        // Start the animation loop
        animationStartTime = 0;
        currentAnimationId = requestAnimationFrame(animateStep);
        // Use string concatenation for console log to avoid f-string issues in JS part
        console.log("Starting animation for " + nodesToAnimate.length + " nodes and " + edgesToAnimate.length + " edges.");
    }} // End function body }}

    // --- Modified Function to Highlight Path ---
    function highlightPath(productId) {{ // Start function body {{
        // Use string concatenation for console log
        console.log("Highlighting path for product: " + productId);
        const data = pathData[productId];
        if (!data) {{ // Start if {{
            console.error("No path data found for product: " + productId);
            return;
        }} // End if }}

        let targetNodeStyles = {{}}; // JS object literal {{}}
        let targetEdgeStyles = {{}}; // JS object literal {{}}

        // Define target styles for path nodes
        data.nodes.forEach(nodeId => {{ // Start forEach arrow function {{
            const baseStyle = baseNodeStyles[nodeId];
            if (!baseStyle) return; // Skip if no base style

            let highlightStyle;
            if (data.bottlenecks.includes(nodeId)) {{ // Start if {{
                highlightStyle = JSON.parse(JSON.stringify(highlightBottleneckStyleDef)); // Deep copy
            }} else {{ // Start else {{
                highlightStyle = JSON.parse(JSON.stringify(highlightNodeStyleDef)); // Deep copy
            }} // End if/else }}
            highlightStyle.size = baseStyle.size * nodeSizeFactor; // Adjust size in target
            targetNodeStyles[nodeId] = highlightStyle;
        }}); // End forEach arrow function }}

        // Define target styles for path edges
        data.optimal_edges.forEach(edgeId => {{ // Start forEach arrow function {{
            if (baseEdgeStyles[edgeId]) {{ // Ensure edge exists in base styles {{
                targetEdgeStyles[edgeId] = JSON.parse(JSON.stringify(highlightEdgeOptimalStyleDef)); // Deep copy
            }} // End if }}
        }}); // End forEach arrow function }}
        data.product_edges.forEach(edgeId => {{ // Start forEach arrow function {{
            if (baseEdgeStyles[edgeId]) {{ // Start if {{
                targetEdgeStyles[edgeId] = JSON.parse(JSON.stringify(highlightEdgeProductStyleDef)); // Deep copy
            }} // End if }}
        }}); // End forEach arrow function }}

        // Start animation TO the calculated target styles
        startAnimation(targetNodeStyles, targetEdgeStyles);
    }} // End function body }}

    // --- Modified Function to Reset Highlights ---
    function resetHighlighting() {{ // Start function body {{
        console.log("Resetting highlights via animation.");
        // Animate TO the base styles (pass empty maps, startAnimation uses base as default)
        startAnimation({{}}, {{}}); // JS object literal {{}}
    }} // End function body }}

    // --- Click Event Listener (Unchanged logic, uses modified functions) ---
    network.on("click", function (params) {{ // Start function body {{
        if (params.nodes.length === 0 && params.edges.length === 0) {{ // Start if {{
            resetHighlighting(); // Animate back to base
            return;
        }} // End if }}
        if (params.nodes.length > 0) {{ // Start if {{
            const clickedNodeId = params.nodes[0];
            // Check network data exists before getting node data
             if (!network || !network.body || !network.body.data || !network.body.data.nodes) return;
            const nodeData = network.body.data.nodes.get(clickedNodeId);
            const nodeType = nodeData?.type;

            if (nodeType === 'product') {{ // Start if {{
                 highlightPath(clickedNodeId); // Animate to highlight
             }} else {{ // Start else {{
                 resetHighlighting(); // Animate back to base
             }} // End if/else }}
        }} else {{ // Start else {{
             resetHighlighting(); // Animate back to base
        }} // End if/else }}
    }}); // End function body }}

    // Apply initial styles directly after a brief pause (Unchanged)
    console.log("Applying initial base styles directly after script load.");
    setTimeout(applyBaseStyles, 100); // Increased timeout slightly just in case

</script>
"""
    # *** END OF JAVASCRIPT DEFINITION ***

    # --- (Step 6: Inject JavaScript into HTML String - MODIFIED FOR DJANGO) ---
    print("Django View: Injecting JavaScript into HTML string...")
    final_html_content = base_html_content # Start with base HTML
    try:
        soup = BeautifulSoup(base_html_content, 'html.parser')
        body = soup.find('body')
        if body:
            # Clean the JS code for injection (remove outer script tags)
            js_code_to_inject = javascript_code.strip()
            if js_code_to_inject.startswith('<script type="text/javascript">'):
                js_code_to_inject = js_code_to_inject[len('<script type="text/javascript">'):]
            if js_code_to_inject.endswith('</script>'):
                 js_code_to_inject = js_code_to_inject[:-len('</script>')]

            script_tag = soup.new_tag('script', type='text/javascript')
            script_tag.string = js_code_to_inject # Inject the cleaned JS code
            body.append(script_tag) # Append to the end of body
            final_html_content = str(soup) # Get the modified HTML string
            print("Django View: JavaScript injected successfully.")
        else:
            print("Django View: Warning: Could not find <body> tag in base HTML. JS not injected.")
            # Keep final_html_content as base_html_content

    except Exception as e:
        print(f"Django View: An error occurred during HTML processing for JS injection: {e}")
        # Decide how to handle: serve base HTML, show error, etc.
        # For now, we'll serve the potentially unmodified base_html_content

    # --- Pass the final HTML to the template ---
    context = {
        'graph_html': final_html_content
    }
    # Use the template name defined in Step 4
    return render(request, 'optimization/graph.html', context)