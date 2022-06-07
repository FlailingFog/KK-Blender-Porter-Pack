#ok now fill it in
translation_dictionary = {
    'bake_mult'     : 'Bake multiplier:',
    'bake_mult_tt'  : "Set this to 2 or 3 if the baked texture is blurry"

    }

def t(text_entry):
    try:
        return translation_dictionary[text_entry]
    except:
        return ''

