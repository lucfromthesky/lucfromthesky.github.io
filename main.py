import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_scrutin_links(main_url):
    response = requests.get(main_url)
    if response.status_code != 200:
        print(f"Erreur : {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    links = soup.find_all("a", class_="link h6")
    base_url = "https://www.assemblee-nationale.fr"
    return [{"url": base_url + link["href"], "title": link.text} for link in links]


def get_list_from_vote_type(li, soup, scrutins, scrutin_url, vote_type, scrutin_title):
    ul = li.find("ul")
    if ul:
        for deputy_li in ul.find_all("li"):
            deputy_name = deputy_li.find("a").text.strip()
            h1 = soup.find("h1").text.strip() if soup.find("h1") else ""
            h2 = soup.find("h2").text.strip() if soup.find("h2") else ""
            amendement_links = []
            for a_tag in soup.find_all("a", class_="inner"):
                href = a_tag.get("href", "")
                if "amendements" in href:
                    amendement_links.append(href)
            scrutins.append(
                {
                    "Lien": scrutin_url,
                    "Titre": h1,
                    "Sous-titre": h2,
                    "Description": scrutin_title,
                    "Député": deputy_name,
                    "Vote": vote_type,
                    "Amendements": amendement_links,
                }
            )


def get_scrutin_data(scrutin_url, scrutin_title):
    response = requests.get(scrutin_url)
    if response.status_code != 200:
        print(f"Erreur : {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    scrutins = []

    for group_li in soup.find_all("li", attrs={"data-organe-id": "PO800520"}):
        for vote_li in group_li.find_all("li", class_="relative-flex _vertical"):
            vote_type = vote_li.find("span", class_="h6").text.strip()
            if vote_type == "Pour":
                get_list_from_vote_type(
                    vote_li, soup, scrutins, scrutin_url, "Pour", scrutin_title
                )
            elif vote_type == "Contre":
                get_list_from_vote_type(
                    vote_li, soup, scrutins, scrutin_url, "Contre", scrutin_title
                )

    return scrutins


main_url = "https://www.assemblee-nationale.fr/dyn/16/scrutins?limit=100"
scrutin_links = get_scrutin_links(main_url)

scrutins_data = []
for link in scrutin_links:
    scrutins = get_scrutin_data(link["url"], link["title"])
    if scrutins:
        scrutins_data.extend(scrutins)


df = pd.DataFrame(scrutins_data)

scrutins_data = set()

votes_count = {}

for _, row in df.iterrows():
    scrutin_key = (row["Titre"], row["Sous-titre"], row["Description"], row["Lien"])
    if scrutin_key not in votes_count:
        votes_count[scrutin_key] = {"Pour": 0, "Contre": 0}

    votes_count[scrutin_key][row["Vote"]] += 1

    scrutins_data.add(
        (
            row["Titre"],
            row["Sous-titre"],
            row["Description"],
            row["Lien"],
            row["Député"],
            row["Vote"],
            row["Amendements"],
        )
    )


scrutins_data = sorted(list(scrutins_data), key=lambda x: x[0])

with open("index.html", "w", encoding="utf-8") as file:
    file.write("<!DOCTYPE html>\n")
    file.write('<html lang="fr">\n')
    file.write("<head>\n")
    file.write('    <meta charset="UTF-8">\n')
    file.write(
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
    )
    file.write("    <title>Votes du Rassemblement National</title>\n")
    file.write(f'<link rel="shortcut icon" href="logo.png" type="image/x-icon">\n')
    file.write(
        '    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">\n'
    )
    file.write("    <style>\n")
    file.write("        body {\n")
    file.write("            font-family: Arial, sans-serif;\n")
    file.write("            line-height: 1.6;\n")
    file.write("            margin: 0;\n")
    file.write("            padding: 20px;\n")
    file.write("            background-color: #f4f4f4;\n")
    file.write("        }\n")
    file.write("        .container {\n")
    file.write("            max-width: 800px;\n")
    file.write("            margin: auto;\n")
    file.write("            background: #fff;\n")
    file.write("            padding: 20px;\n")
    file.write("            border-radius: 8px;\n")
    file.write("            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);\n")
    file.write("        }\n")
    file.write("        h1 {\n")
    file.write("            text-align: center;\n")
    file.write("            color: #333;\n")
    file.write("        }\n")
    file.write("        .scrutin {\n")
    file.write("            margin-bottom: 20px;\n")
    file.write("            padding-bottom: 10px;\n")
    file.write("            border-bottom: 1px solid #ccc;\n")
    file.write("        }\n")
    file.write("        .scrutin a {\n")
    file.write("            color: #007bff;\n")
    file.write("            text-decoration: none;\n")
    file.write("        }\n")
    file.write("        .scrutin a:hover {\n")
    file.write("            text-decoration: underline;\n")
    file.write("        }\n")
    file.write("        .underline {\n")
    file.write("            text-decoration: underline;\n")
    file.write("        }\n")
    file.write("        .success {\n")
    file.write("            background-color: #d4edda;\n")
    file.write("            color: #155724;\n")
    file.write("        }\n")
    file.write("        .danger {\n")
    file.write("            background-color: #f8d7da;\n")
    file.write("            color: #721c24;\n")
    file.write("        }\n")
    file.write("        .marquor {\n")
    file.write("            height: 20px;\n")
    file.write("        }\n")
    file.write("    </style>\n")
    file.write("</head>\n")
    file.write("<body>\n")
    file.write('    <div class="container">\n')
    file.write("        <h1>Votes des Députés du Rassemblement National</h1>\n")
    file.write(
        "        <p>Cette page présente les 100 derniers scrutins à l'Assemblée nationale, en mettant en évidence les votes des députés du Rassemblement National (RN). Vous trouverez ici les noms des députés, leur vote (pour ou contre), ainsi que des liens vers les projets de loi correspondants pour mieux comprendre le contexte.</p>\n"
    )
    file.write(
        f"<div class='mb-3'><span class='underline'>Source</span> : <a href='https://www.assemblee-nationale.fr/' target='_blank'>Assemblée Nationale</a></div>"
    )

    file.write('<div class="accordion" id="accordionExample">\n')

    for i, (titre, sous_titre, description, lien) in enumerate(votes_count.keys()):
        pour_count = votes_count[(titre, sous_titre, description, lien)]["Pour"]
        contre_count = votes_count[(titre, sous_titre, description, lien)]["Contre"]
        class_name = "success" if pour_count > contre_count else "danger"

        file.write(f'    <div class="card mb-3 rounded shadow">\n')
        file.write(f"<div class='{class_name} marquor'></div>")
        file.write(f'        <div class="card-header" id="heading{i}">\n')
        file.write("            <p>\n")
        file.write(
            f'                <a class="link" type="button" data-toggle="collapse" data-target="#collapse{i}" aria-expanded="true" aria-controls="collapse{i}">\n'
        )
        file.write(f"                    {titre} - {sous_titre}\n")
        file.write("                </a>\n")
        file.write("            </p>\n")
        file.write(
            f'            <p>{description} <a href="{lien}" target="_blank">Lire plus</a></p>\n'
        )
        file.write(f"               <h5 class='mt-3 mb-3 underline'>Total Votes</h5>\n")
        file.write('                <table class="table">\n')
        file.write("                    <thead>\n")
        file.write("                        <tr>\n")
        file.write(
            '                            <th scope="col" class="table-success">Pour</th>\n'
        )
        file.write(
            '                            <th scope="col" class="table-danger">Contre</th>\n'
        )
        file.write("                        </tr>\n")
        file.write("                    </thead>\n")
        file.write("                    <tbody>\n")

        file.write("                        <tr>\n")
        file.write(f"                            <td>{pour_count}</td>\n")
        file.write(f"                            <td>{contre_count}</td>\n")
        file.write("                        </tr>\n")

        file.write("                    </tbody>\n")
        file.write("                </table>\n")

        file.write("        </div>\n")

        file.write(
            '        <div id="collapse{0}" class="collapse" aria-labelledby="heading{0}" data-parent="#accordionExample">\n'.format(
                i
            )
        )
        file.write('            <div class="card-body">\n')
        file.write('                <table class="table">\n')
        file.write("                    <thead>\n")
        file.write("                        <tr>\n")
        file.write('                            <th scope="col">Député</th>\n')
        file.write('                            <th scope="col">Vote</th>\n')
        file.write("                        </tr>\n")
        file.write("                    </thead>\n")
        file.write("                    <tbody>\n")

        for scrutin in scrutins_data:
            if (
                scrutin[0] == titre
                and scrutin[1] == sous_titre
                and scrutin[2] == description
                and scrutin[3] == lien
            ):
                vote_class = "text-success" if scrutin[5] == "Pour" else "text-danger"
                file.write("                        <tr>\n")
                file.write(f"                            <td>{scrutin[4]}</td>\n")
                file.write(
                    f'                            <td class="{vote_class}">{scrutin[5]}</td>\n'
                )
                file.write("                        </tr>\n")

        file.write("                    </tbody>\n")
        file.write("                </table>\n")

        if scrutin[6]:
            file.write('                <div class="amendements">\n')
            file.write(
                "                    <p><span class='underline'>Amendement</span> :</p>\n"
            )
            file.write("                    <ul>\n")
            amendements_list = eval(scrutin[6])
            for amendement in amendements_list:
                file.write(
                    f'                        <li><a href="{amendement}" target="_blank">Amendement n°{amendement.split("/")[-1]}</a></li>\n'
                )
            file.write("                    </ul>\n")
            file.write("                </div>\n")

        file.write("            </div>\n")
        file.write("        </div>\n")
        file.write("    </div>\n")

    file.write("</div>\n")
    file.write("    </div>\n")
    file.write(
        '    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>\n'
    )
    file.write(
        '    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.2/dist/umd/popper.min.js"></script>\n'
    )
    file.write(
        '    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>\n'
    )
    file.write("</body>\n")
    file.write("</html>\n")
