'use server';

import { z } from 'zod';
import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';

const FormSchema = z.object({
  id: z.string(),
  customerId: z.string({
    invalid_type_error: 'Please select a customer.',
  }),
  amount: z.coerce
    .number()
    .gt(0, { message: 'Please enter an amount greater than $0.' }),
  status: z.enum(['pending', 'paid'], {
    invalid_type_error: 'Please select an invoice status.',
  }),
  date: z.string(),
});

const CreateInvoice = FormSchema.omit({ id: true, date: true });
const UpdateInvoice = FormSchema.omit({ id: true, date: true });

export type State = {
  errors?: {
    customerId?: string[];
    amount?: string[];
    status?: string[];
  };
  message?: string | null;
};

export async function createInvoice(prevState: State, formData: FormData) {
  // Validate form using Zod
  const validatedFields = CreateInvoice.safeParse({
    customerId: formData.get('customerId'),
    amount: formData.get('amount'),
    status: formData.get('status'),
  });

  // If form validation fails, return errors early. Otherwise, continue.
  if (!validatedFields.success) {
    return {
      errors: validatedFields.error.flatten().fieldErrors,
      message: 'Missing Fields. Failed to Create Invoice.',
    };
  }

  // Prepare data for insertion into the database
  const { customerId, amount, status } = validatedFields.data;
  const amountInCents = amount * 100;
  const date = new Date().toISOString().split('T')[0];

  // Insert data into the database
  try {
    ///////////////
  } catch (error) {
    // If a database error occurs, return a more specific error.
    return {
      message: 'Database Error: Failed to Create Invoice.',
    };
  }

  // Revalidate the cache for the invoices page and redirect the user.
  revalidatePath('/dashboard/invoices');
  redirect('/dashboard/invoices');
}

export async function updateInvoice(
  id: string,
  prevState: State,
  formData: FormData,
) {
  const validatedFields = UpdateInvoice.safeParse({
    customerId: formData.get('customerId'),
    amount: formData.get('amount'),
    status: formData.get('status'),
  });

  if (!validatedFields.success) {
    return {
      errors: validatedFields.error.flatten().fieldErrors,
      message: 'Missing Fields. Failed to Update Invoice.',
    };
  }

  const { customerId, amount, status } = validatedFields.data;
  const amountInCents = amount * 100;

  try {
    /////////////////
  } catch (error) {
    return { message: 'Database Error: Failed to Update Invoice.' };
  }

  revalidatePath('/dashboard/invoices');
  redirect('/dashboard/invoices');
}

export async function deleteRoom(roomId: number) {
  const requestOptions = {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      id: roomId,
    })
  };

  return fetch(`${process.env.NEXT_PUBLIC_API_URL}/rooms`, requestOptions)
    .then(async () => {
      return { message: 'Deleted Room.' };
    }).catch(err => {
      return { message: 'Database Error: Failed to Delete Room.', error: err };
    })
}

export async function importRooms(formData: FormData) {
  try {
    const file: File = formData.get('file') as File;
  
    console.log(`placeholder: ${file.name}`)
    revalidatePath('/rooms');
    
    // Create a new FormData object and append the file
    const formDataToSend = new FormData();
    formDataToSend.append('database', file);

    // Define the request options with method and body as FormData
    const requestOptions = {
      method: 'POST',
      body: formDataToSend
    };

    return fetch(`${process.env.NEXT_PUBLIC_API_URL}/data`, requestOptions)
      .then(async (res) => res.json())
      .catch(err => {
        console.error('Database Error: Failed to Get Rooms.');
        console.error(err)
      })
    // return { message: 'Rooms Imported Successfully.' };
  } catch (error) {
    // return { message: 'Database Error: Failed to Import Rooms.' };
  }
}