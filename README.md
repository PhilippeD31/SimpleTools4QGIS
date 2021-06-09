# Simple tools -- Couteau suisse pour QGIS
**A plugin for QGIS**  
A collection of simple tools for QGIS :  
-- Categorized style from CSV  
-- Inspect BIG csv (or text) files by quickly showing their first rows  
-- Convert JSON to CSV: flatten a json tree

<table border=1 cellpadding=3 cellspacing=0>
 <thead>
	<tr style="text-align:center"><th>JSON</th><th>CSV</th></tr>
 </thead>
	<tr> <td> [<br>&nbsp;&nbsp; {"id":1, "color":"red"},<br>&nbsp;&nbsp; {"id":2, "color":"blue"}<br> ]</td>
		<td>id,color<br>1,red<br>2,blue</td>
	</tr>
	<tr> <td> { "id":123, <b>"contact": {"tel":555, "mail":"a@b.c"}</b> }</td>
		<td>id;<b>contact_tel</b>;<b>contact_mail</b><br>123;555;a@b.c</td>
	</tr>
	<tr> <td> { "shades":<br>&nbsp;&nbsp; [<br>&nbsp;&nbsp;&nbsp;&nbsp; {"id":1, "color":"red"},<br>&nbsp;&nbsp;&nbsp;&nbsp; {"id":2, "color":"blue"}<br>&nbsp;&nbsp; ]<br>} </td>
		<td>shades,shades_id,shades_color<br>,1,red<br>,2,blue</td>
	</tr>
</table>

**FR : une extension pour QGIS**  
Conçu comme une collection d'outils simples. Une sorte de "couteau suisse" pour QGIS :  
-- Style catégorisé à partir d'un CSV  
-- Inspecter les 1ères lignes d'un GROS fichier CSV ou texte : affichage très rapide  
-- Convertir du JSON en CSV : mettre à plat une arborescence json  
