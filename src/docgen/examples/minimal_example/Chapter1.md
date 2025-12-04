
# Résumé du chapitre 1

Il s'agit d'une chapitre à plusieurs titres.

On démontre ici le recours :

- à des variables 
- à des sous partie impbriqués
- à des styles personnalisé (word ou css)


# {{< var section1_title >}}

Je suis une premier titre. A l'intérieur, on trouve 

- une sous partie qui respecte un style,
- une image

::: {custom-style="Questions"}
Ceci doit utiliser le style `Questions`.
:::

![image](image_at_root.png)

![outer_image](../outer_image.png)

{{< excel coucou  >}}


# Second titre

{{< include Chapter1_nested_part.md >}}



Vars {{< meta vars>}}

::: {.content-hidden when-meta="vars.hide_3"}

# Troisième titre conditionnel

{{< meta vars.hide_3>}}
{{< var hide_3>}}


:::

::: {.content-hidden unless-meta="vars.hide_3"}

# Troisième titre conditionnel si hide_3

{{< meta vars.hide_3>}}
{{< var hide_3>}}

:::



{% for valeur in une_liste%}

## Sous paragraphe {{valeur}}

Créé par itération
{% endfor %}



<h1>Cinquième § html<h1>