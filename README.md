let
    Baza = "https:///moam.nsf/mOAM?readForm&RestrictToCategory=",
    DniWstecz = 7,

    fnDzien = (d as date) as table =>
        let
            Url = Baza & Date.ToText(d, "yyyy-MM-dd") & "&start=1&count=1000",
            Src = Web.Page(Web.Contents(Url)),
            Tabele = List.Select(Src[Data], each Table.ColumnCount(_) >= 3 and Table.RowCount(_) > 0),
            Najw = List.Max(Tabele, null, each Table.RowCount(_)),
            Nazwy = List.FirstN(Table.ColumnNames(Najw), 3),
            Trzy = Table.SelectColumns(Najw, Nazwy),
            Gotowe = Table.RenameColumns(Trzy, List.Zip({Nazwy, {"Emitent", "Data wpływu", "Tytuł raportu"}}))
        in
            Gotowe,

    Dni = List.Transform({0..DniWstecz-1}, each Date.AddDays(Date.From(DateTime.LocalNow()), -_)),
    Pobrane = List.Transform(Dni, each try fnDzien(_) otherwise null),
    Polaczone = Table.Combine(List.Select(Pobrane, each _ <> null)),
    BezNaglowkow = Table.SelectRows(Polaczone, each [Emitent] <> "Emitent" and [Tytuł raportu] <> null),

    Norm = Table.AddColumn(BezNaglowkow, "tmp", each
        Text.Remove(Text.Lower(Text.From([Tytuł raportu])), {" ", ".", "#(00A0)", "-", "_"}), type text),

    Filtr = Table.SelectRows(Norm, each
        Text.Contains([tmp], "art69") or Text.Contains([tmp], "art70") or
        Text.Contains([tmp], "artykuł69") or Text.Contains([tmp], "artykułu69") or
        Text.Contains([tmp], "artykuł70") or Text.Contains([tmp], "artykułu70")),

    Wynik = Table.Sort(Table.RemoveColumns(Filtr, {"tmp"}), {{"Data wpływu", Order.Descending}})
in
    Wynik
