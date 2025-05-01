from math import ceil
from flask import Flask, render_template, request
import importlib

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    results = {}
    paginated_results = []
    page = int(request.args.get("page", 1))
    per_page = 20
    total_pages = 0

    # Get parameters from form or URL
    rank = request.form.get("rank") or request.args.get("rank")
    category_input = request.form.get("category") or request.args.get("category")
    round_selected = request.form.get("round") or request.args.get("round")
    branch_selected = request.form.get("branch") or request.args.get("branch", "all")

    if rank and category_input and round_selected and branch_selected:
        try:
            rank = int(rank)
            data_module = importlib.import_module(f"data.round{round_selected}")
            data = data_module.data
            keyword = branch_selected.lower() if branch_selected.lower() != "all" else ""

            for entry in data:
                try:
                    closing_rank = int(entry["ClosingRank"])
                    entry_category = entry["Category"]
                    entry_branch = entry["ProgramName"]
                    if (
                        rank <= closing_rank
                        and entry["SeatTypeName"] == "WBJEE Seats"
                        and (not keyword or keyword in entry_branch.lower())
                        and entry_category == category_input
                    ):  
                        college = entry["InstituteName"]
                        branch = entry["ProgramName"]
                        if college not in results:
                            results[college] = set()
                        results[college].add(branch)
                except ValueError:
                    continue

            # Pagination logic
            result_items = list(results.items())
            total_pages = ceil(len(result_items) / per_page)
            start = (page - 1) * per_page
            end = start + per_page
            paginated_results = result_items[start:end]

        except Exception as e:
            print("Error:", e)

    return render_template(
        "index.html",
        results=results,
        paginated_results=paginated_results,
        current_page=page,
        total_pages=total_pages,
        rank=rank,
        category=category_input,
        round_selected=round_selected,
        branch_selected=branch_selected
    )

if __name__ == "__main__":
    app.run(debug=True)