# Autogenerated file
def render(info, plugindata):
    yield """
    """
    for cnt in range(1,plugindata['valuecnt']+1):
        yield """
        <TR>
           <TH>Value Setting """
        yield str(cnt)
        yield """
           <TH>Value 
        <TR>
           <TD>Name: 
           <TD><input type='text' name='valueN"""
        yield str(cnt)
        yield """' maxlength='40' value='"""
        yield str(plugindata['valueN'+str(cnt)])
        yield """'>
        <TR>
           <TD>Formula:
           <TD><input type='text' name='valueF"""
        yield str(cnt)
        yield """' maxlength='40' value='"""
        yield str(plugindata['valueF'+str(cnt)])
        yield """'>
           <a class=\"button link\" href=\"\" target=\"_blank\">?</a>
        <TR>
           <TD>Decimals:
           <TD><input type='number' name='valueD"""
        yield str(cnt)
        yield """' min=0 max=6 style='width:5em;' value='"""
        yield str(plugindata['valueD'+str(cnt)])
        yield """'>
    """
    yield """
    <TR>
       <TD colspan='2'>
          <hr>
    <TR>
       <TD>
       <TD><a class=\"button link\" href=\"devices\">Close</a><input class=\"button link\" type='submit' value='Submit'>
    </table>
    </form>
"""
