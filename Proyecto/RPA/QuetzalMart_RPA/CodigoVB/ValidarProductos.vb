' =====================================================================================
' Invoke Code: ValidarProductos   (QuetzalMart_RPA / Workflows/ProcesarArchivos.xaml)
' Argumentos:
'   dtHoja      (In)  DataTable  -> hoja "productos" leida con Read Range (AddHeaders=True)
'   archivo     (In)  String     -> ruta relativa del Excel (para el log)
'   hoja        (In)  String     -> nombre real de la hoja
'   versionOdoo (In)  String     -> "18" o "17" (en v18 se incluye is_storable)
'   ubicacion   (In)  String     -> nombre de ubicacion de inventario (ej. "WH/Stock")
'   dtPro       (In)  DataTable  -> consolidado de productos (se llena)
'   dtInv       (In)  DataTable  -> lineas de ajuste de inventario (se llena)
'   dtLog       (In)  DataTable  -> log de filas rechazadas / advertencias (se llena)
' Reglas:
'   * Obligatorios: External ID (id), Name, Product Type.
'   * Numericos no negativos: Sales Price, Cost, Weight, Cantidad a la mano.
'   * Está publicado: booleano (True/False).
'   * Duplicados: ID externo unico, Barcode unico (si viene).
'   * Servicios no manejan inventario (se advierte si traen cantidad y no se carga a stock).
' =====================================================================================
Dim inv As System.Globalization.CultureInfo = System.Globalization.CultureInfo.InvariantCulture

Dim norm As Func(Of String, String) = Function(s As String) As String
    If s Is Nothing Then Return ""
    Dim t As String = s.Replace("*", "").Trim().ToLowerInvariant().Normalize(System.Text.NormalizationForm.FormD)
    Dim sb As New System.Text.StringBuilder()
    For Each ch As Char In t
        If System.Globalization.CharUnicodeInfo.GetUnicodeCategory(ch) <> System.Globalization.UnicodeCategory.NonSpacingMark Then sb.Append(ch)
    Next
    Return sb.ToString()
End Function

Dim txt As Func(Of Object, String) = Function(o As Object) As String
    If o Is Nothing OrElse TypeOf o Is DBNull Then Return ""
    If TypeOf o Is Boolean Then Return If(CBool(o), "True", "False")
    If TypeOf o Is Double Then
        Dim d As Double = CDbl(o)
        If d = Math.Floor(d) AndAlso Math.Abs(d) < 1.0E+15 Then Return CLng(d).ToString(inv)
        Return d.ToString(inv)
    End If
    Return o.ToString().Trim()
End Function

Dim parseNum As Func(Of String, Tuple(Of Boolean, Double?)) = Function(s As String) As Tuple(Of Boolean, Double?)
    If String.IsNullOrWhiteSpace(s) Then Return Tuple.Create(True, CType(Nothing, Double?))
    Dim limpio As String = s.Replace(",", "").Trim()
    Dim val As Double
    If Double.TryParse(limpio, System.Globalization.NumberStyles.Any, inv, val) Then
        Return Tuple.Create(True, CType(val, Double?))
    Else
        Return Tuple.Create(False, CType(Nothing, Double?))
    End If
End Function

Dim fmtNum As Func(Of Double?, String) = Function(d As Double?) As String
    If Not d.HasValue Then Return ""
    If d.Value = Math.Floor(d.Value) AndAlso Math.Abs(d.Value) < 1.0E+15 Then
        Return CLng(d.Value).ToString(inv)
    End If
    Return d.Value.ToString(inv)
End Function

' ---- campos y alias aceptados
Dim campos As String() = {"id", "name", "type", "default_code", "barcode", "list_price", "standard_price", "weight", "description_sale", "product_values", "qty", "is_published"}
Dim aliases As New Dictionary(Of String, String())
aliases("id") = {"external id", "id externo", "id"}
aliases("name") = {"name", "nombre"}
aliases("type") = {"product type", "tipo de producto", "tipo"}
aliases("default_code") = {"internal reference", "referencia interna", "referencia"}
aliases("barcode") = {"barcode", "codigo de barras"}
aliases("list_price") = {"sales price", "precio de venta", "precio"}
aliases("standard_price") = {"cost", "costo"}
aliases("weight") = {"weight", "peso"}
aliases("description_sale") = {"sales description", "descripcion de venta", "descripcion"}
aliases("product_values") = {"product values", "valores del producto"}
aliases("qty") = {"cantidad a la mano", "quantity on hand", "cantidad"}
aliases("is_published") = {"esta publicado", "is published", "publicado"}

Dim verdaderos As New HashSet(Of String)(New String() {"true", "verdadero", "si", "yes", "1", "x", "publicado"})
Dim falsos As New HashSet(Of String)(New String() {"false", "falso", "no", "0", "no publicado", ""})

Dim mapa As New Dictionary(Of String, String)
For Each col As System.Data.DataColumn In dtHoja.Columns
    Dim n As String = norm(col.ColumnName)
    For Each campo As String In campos
        If Not mapa.ContainsKey(campo) AndAlso Array.IndexOf(aliases(campo), n) >= 0 Then mapa(campo) = col.ColumnName
    Next
Next

Dim faltan As New List(Of String)
For Each c As String In New String() {"id", "name", "type"}
    If Not mapa.ContainsKey(c) Then faltan.Add(c)
Next

If faltan.Count > 0 Then
    dtLog.Rows.Add("RECHAZADO", "Producto", archivo, hoja, "1", "(encabezado)", "Faltan columnas obligatorias: " & String.Join(", ", faltan))
Else
    ' Claves ya consolidadas previamente
    Dim idsExistentes As New Dictionary(Of String, Boolean)
    Dim barcodesExistentes As New Dictionary(Of String, Boolean)
    For Each r As System.Data.DataRow In dtPro.Rows
        idsExistentes(r("id").ToString().ToLowerInvariant()) = True
        If r.Table.Columns.Contains("barcode") AndAlso r("barcode").ToString() <> "" Then
            barcodesExistentes(r("barcode").ToString()) = True
        End If
    Next

    For i As Integer = 0 To dtHoja.Rows.Count - 1
        Dim fila As Integer = i + 2
        Dim row As System.Data.DataRow = dtHoja.Rows(i)
        Dim d As New Dictionary(Of String, String)
        Dim vacia As Boolean = True
        For Each campo As String In campos
            d(campo) = If(mapa.ContainsKey(campo), txt(row(mapa(campo))), "")
            If d(campo) <> "" Then vacia = False
        Next

        If Not vacia Then
            Dim ident As String = If(d("id") <> "", d("id"), If(d("name") <> "", d("name"), "(sin identificador)"))
            Dim errores As New List(Of String)
            Dim avisos As New List(Of String)

            If d("id") = "" Then errores.Add("External ID vacío")
            If d("name") = "" Then errores.Add("Name vacío")

            Dim pt As String = norm(d("type"))
            Dim esBien As Boolean = False
            If pt = "" Then
                errores.Add("Product Type vacío")
            ElseIf pt = "goods" OrElse pt = "consumable" OrElse pt = "storable product" OrElse pt = "storable" OrElse pt = "product" OrElse pt = "bien" OrElse pt = "bienes" OrElse pt = "consumible" OrElse pt = "almacenable" Then
                esBien = True
                d("type") = If(versionOdoo >= "18", "Goods", "Storable Product")
            ElseIf pt = "service" OrElse pt = "servicio" Then
                d("type") = "Service"
            ElseIf pt = "combo" Then
                d("type") = "Combo"
            Else
                errores.Add("Product Type inválido '" & d("type") & "'")
            End If

            ' Validaciones numéricas
            Dim numCampos As Tuple(Of String, String)() = {
                Tuple.Create("list_price", "Sales Price"),
                Tuple.Create("standard_price", "Cost"),
                Tuple.Create("weight", "Weight"),
                Tuple.Create("qty", "Cantidad a la mano")
            }
            For Each nc In numCampos
                Dim res = parseNum(d(nc.Item1))
                If Not res.Item1 Then
                    errores.Add(nc.Item2 & " no numérico '" & d(nc.Item1) & "'")
                ElseIf res.Item2.HasValue AndAlso res.Item2.Value < 0 Then
                    errores.Add(nc.Item2 & " negativo (" & fmtNum(res.Item2) & ")")
                Else
                    d(nc.Item1) = fmtNum(res.Item2)
                End If
            Next

            ' Barcode
            If d("barcode") <> "" Then
                Dim bRes = parseNum(d("barcode"))
                If bRes.Item1 AndAlso bRes.Item2.HasValue Then
                    d("barcode") = CLng(Math.Round(bRes.Item2.Value)).ToString(inv)
                End If
            End If

            ' Publicado
            Dim pubNorm As String = norm(d("is_published"))
            If verdaderos.Contains(pubNorm) Then
                d("is_published") = "True"
            ElseIf falsos.Contains(pubNorm) Then
                d("is_published") = "False"
            Else
                errores.Add("Está publicado inválido '" & d("is_published") & "' (Sí/No)")
            End If

            ' Duplicados
            If errores.Count = 0 AndAlso idsExistentes.ContainsKey(d("id").ToLowerInvariant()) Then
                errores.Add("External ID duplicado '" & d("id") & "'")
            End If
            If errores.Count = 0 AndAlso d("barcode") <> "" AndAlso barcodesExistentes.ContainsKey(d("barcode")) Then
                errores.Add("Barcode duplicado '" & d("barcode") & "'")
            End If

            If errores.Count > 0 Then
                dtLog.Rows.Add("RECHAZADO", "Producto", archivo, hoja, fila.ToString(), ident, String.Join("; ", errores))
            Else
                ' Advertencias no bloqueantes
                If d("product_values") <> "" Then
                    avisos.Add("Product Values se ignora en la importación web")
                End If
                If Not esBien AndAlso d("qty") <> "" AndAlso d("qty") <> "0" Then
                    avisos.Add("Cantidad " & d("qty") & " ignorada: un producto de tipo servicio no maneja inventario")
                    d("qty") = ""
                End If

                For Each av In avisos
                    dtLog.Rows.Add("ADVERTENCIA", "Producto", archivo, hoja, fila.ToString(), ident, av)
                Next

                idsExistentes(d("id").ToLowerInvariant()) = True
                If d("barcode") <> "" Then barcodesExistentes(d("barcode")) = True

                ' Fila para dtPro
                Dim nr As System.Data.DataRow = dtPro.NewRow()
                nr("id") = d("id")
                nr("name") = d("name")
                nr("type") = d("type")
                nr("default_code") = d("default_code")
                nr("barcode") = d("barcode")
                nr("list_price") = d("list_price")
                nr("standard_price") = d("standard_price")
                nr("weight") = d("weight")
                nr("description_sale") = d("description_sale")
                nr("is_published") = d("is_published")
                If dtPro.Columns.Contains("is_storable") Then
                    nr("is_storable") = If(esBien, "True", "False")
                End If
                dtPro.Rows.Add(nr)

                ' Fila para ajuste de inventario (solo para productos físicos con stock > 0)
                If esBien AndAlso d("qty") <> "" AndAlso d("qty") <> "0" Then
                    Dim invRow As System.Data.DataRow = dtInv.NewRow()
                    invRow("product_id") = If(d("default_code") <> "", d("default_code"), d("name"))
                    invRow("location_id") = ubicacion
                    invRow("inventory_quantity") = d("qty")
                    dtInv.Rows.Add(invRow)
                End If
            End If
        End If
    Next
End If
