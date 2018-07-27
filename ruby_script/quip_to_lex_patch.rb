#!/usr/bin/env ruby

def lex_patch(type, token, pron)
  if pron =~ /=/
    left_token = pron.split(/ *= */).first.gsub(' ', '_')
    right_pron = pron.split(/ *= */).last
  else
    left_token = token.gsub(' ', '_')
    right_pron = pron
  end
  "LEX\t#{type} #{left_token} #{right_pron}"
end


token_prons = {}

IO.readlines(ARGV[0]).map(&:strip).each do |line|
  token, pron = line.split("\t")

  # data cleansing
  token = token.gsub('·', '').gsub('’', "'")
  pron  = pron.gsub(/ *\(.+/, '')

  if pron =~ /=/
    token = token.gsub(pron.split(/ *= */).first) { |m| " #{m} " }.gsub(/ +/, ' ').strip
  end

  if token_prons.has_key?(token)
    token_prons[token] << pron
  else
    token_prons[token] = [pron]
  end
end

token_prons.keys.sort.each do |token|
  prons = token_prons[token]

  left_token = token.gsub(' ', '_')

  puts lex_patch('ADDTOKEN', token, prons.first)
  if prons.size > 1
    prons[1..-1].each do |pron|
      puts lex_patch('ADDPRON', token, pron)
      # puts "LEX\tADDPRON #{left_token} #{pron}"
    end
  end
end

puts
puts "DAT\t<MEGA_FEED_N> ( #{token_prons.keys.sort.join(' | ')} )"