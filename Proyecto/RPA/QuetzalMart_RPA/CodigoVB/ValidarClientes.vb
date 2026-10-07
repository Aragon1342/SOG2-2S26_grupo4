' =====================================================================================
' Invoke Code: ValidarClientes   (QuetzalMart_RPA / Workflows/ProcesarArchivos.xaml)
' Argumentos:
'   dtHoja   (In)  DataTable  -> hoja "clientes" leida con Read Range (AddHeaders=True)
'   archivo  (In)  String     -> ruta relativa del Excel (para el log)
'   hoja     (In)  String     -> nombre real de la hoja
'   dtCliEmp (In)  DataTable  -> consolidado clientes SIN empresa relacionada (se llena)
'   dtCliPer (In)  DataTable  -> consolidado contactos CON empresa relacionada (se llena)
'   dtLog    (In)  DataTable  -> log de filas rechazadas / advertencias (se llena)
' Reglas:
'   * Obligatorios: Name, Company Type (Person/Company).
'   * Email (si viene) con formato valido.
'   * Duplicado = mismo Name + Email ya consolidado.
'   * Filas completamente vacias se ignoran.
'   * Se genera un External ID (columna id) para poder re-importar sin duplicar.
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

Dim slug As Func(Of String, String) = Function(s As String) As String
    Dim sb As New System.Text.StringBuilder()
    For Each ch As Char In norm(s)
        If (ch >= "a"c AndAlso ch <= "z"c) OrElse (ch >= "0"c AndAlso ch <= "9"c) Then
            sb.Append(ch)
        ElseIf sb.Length > 0 AndAlso sb(sb.Length - 1) <> "_"c Then
            sb.Append("_"c)
        End If
    Next
    Return sb.ToString().Trim("_"c)
End Function

Dim emailOk As Func(Of String, Boolean) = Function(e As String) As Boolean
    If e.Contains(" ") Then Return False
    Dim at As Integer = e.IndexOf("@"c)
    If at <= 0 OrElse at <> e.LastIndexOf("@"c) Then Return False
    Dim dominio As String = e.Substring(at + 1)
    Dim p As Integer = dominio.IndexOf("."c)
    Return p > 0 AndAlso Not dominio.EndsWith(".")
End Function

' ---- campos y alias aceptados (encabezados normalizados: sin *, sin tildes, minusculas)
Dim campos As String() = {"name", "company_type", "parent_id", "email", "phone", "street", "street2", "city", "state_id", "zip", "country_id", "vat", "Enlace del sitio web", "category_id", "ref", "comment"}
Dim aliases As New Dictionary(Of String, String())
aliases("name") = {"name", "nombre"}
aliases("company_type") = {"company type", "tipo de compania", "tipo"}
aliases("parent_id") = {"related company", "empresa relacionada", "compania relacionada"}
aliases("email") = {"email", "correo", "correo electronico"}
aliases("phone") = {"phone", "telefono"}
aliases("street") = {"street", "calle", "direccion"}
aliases("street2") = {"street2", "calle2", "direccion 2"}
aliases("city") = {"city", "ciudad"}
aliases("state_id") = {"state", "estado", "departamento"}
aliases("zip") = {"zip", "codigo postal"}
aliases("country_id") = {"country", "pais"}
aliases("vat") = {"tax id", "nit", "vat"}
aliases("Enlace del sitio web") = {"website", "sitio web", "enlace del sitio web", "enlace web"}
aliases("category_id") = {"tags", "etiquetas"}
aliases("ref") = {"reference", "referencia"}
aliases("comment") = {"notes", "notas"}

Dim mapa As New Dictionary(Of String, String)
For Each col As System.Data.DataColumn In dtHoja.Columns
    Dim n As String = norm(col.ColumnName)
    For Each campo As String In campos
        If Not mapa.ContainsKey(campo) AndAlso Array.IndexOf(aliases(campo), n) >= 0 Then mapa(campo) = col.ColumnName
    Next
Next

Dim faltan As New List(Of String)
For Each c As String In New String() {"name", "company_type"}
    If Not mapa.ContainsKey(c) Then faltan.Add(c)
Next

If faltan.Count > 0 Then
    dtLog.Rows.Add("RECHAZADO", "Cliente", archivo, hoja, "1", "(encabezado)", "Faltan columnas obligatorias: " & String.Join(", ", faltan))
Else
    ' claves ya consolidadas (de hojas/archivos anteriores)
    Dim claves As New Dictionary(Of String, Boolean)
    Dim ids As New Dictionary(Of String, Boolean)
    For Each t As System.Data.DataTable In New System.Data.DataTable() {dtCliEmp, dtCliPer}
        For Each r As System.Data.DataRow In t.Rows
            claves(r("name").ToString().ToLowerInvariant() & "|" & r("email").ToString().ToLowerInvariant()) = True
            ids(r("id").ToString()) = True
        Next
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
            Dim ident As String = If(d("name") <> "", d("name"), "(sin nombre)")
            Dim errores As New List(Of String)
            If d("name") = "" Then errores.Add("Name vacío")

            Dim ct As String = norm(d("company_type"))
            If ct = "" Then
                errores.Add("Company Type vacío")
            ElseIf ct = "person" OrElse ct = "individual" OrElse ct = "persona" Then
                d("company_type") = "person"
            ElseIf ct = "company" OrElse ct = "compania" OrElse ct = "empresa" Then
                d("company_type") = "company"
            Else
                errores.Add("Company Type inválido '" & d("company_type") & "' (Person/Company)")
            End If

            If d("email") <> "" AndAlso Not emailOk(d("email")) Then errores.Add("Email inválido '" & d("email") & "'")

            Dim clave As String = d("name").ToLowerInvariant() & "|" & d("email").ToLowerInvariant()
            If errores.Count = 0 AndAlso claves.ContainsKey(clave) Then errores.Add("Cliente duplicado (mismo Name y Email)")

            If errores.Count > 0 Then
                dtLog.Rows.Add("RECHAZADO", "Cliente", archivo, hoja, fila.ToString(), ident, String.Join("; ", errores))
            Else
                claves(clave) = True
                Dim baseId As String = If(d("ref") <> "", slug(d("ref")), "qm_cli_" & slug(d("name")))
                Dim xid As String = baseId
                Dim k As Integer = 2
                While ids.ContainsKey(xid)
                    xid = baseId & "_" & k.ToString()
                    k += 1
                End While
                ids(xid) = True

                Dim destino As System.Data.DataTable = If(d("parent_id") <> "", dtCliPer, dtCliEmp)
                Dim nr As System.Data.DataRow = destino.NewRow()
                nr("id") = xid
                For Each campo As String In campos
                    nr(campo) = d(campo)
                Next
                destino.Rows.Add(nr)
            End If
        End If
    Next
End If
