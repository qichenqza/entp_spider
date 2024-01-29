# get key word from input file, get FIRST search result and format the result into output file
# the FIRST column of input file should be key word which means (企业名称 / 统一社会信用代码 / 组织机构代码)
# if on result got from FIRST column, will try the SECOND column

#.\entp.exe search --input keyword.xlsx --output entp_output --dump_json

# read url from input file, parse html file of url and format the result into output file
# the FIRST column of input file should be url

 #.\entp.exe url --input url.xlsx --output entp_output --dump_json

$sub_command = $args[0]
$input_file = $args[1]
$output_file = $args[2]

..\dist\entp\entp.exe $sub_command --input_file $input_file --output_file $output_file --dump_json | Tee-Object -FilePath "$output_file.log"

pause